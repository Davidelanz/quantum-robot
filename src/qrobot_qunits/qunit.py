import json
from collections.abc import Generator
import redis

from qrobot.bursts import Burst
from qrobot.logger import LoggingConfig
from qrobot.models import Model
from . import redis_utils
from .base import BaseUnit
from .redis_utils import RedisConfig, RedisWriteError


class QUnit(BaseUnit):
    """Periodically process coupled inputs through a quantum-like model.

    A qUnit reads its inputs from Redis, encodes them over the model's
    temporal window, applies a query, and publishes the resulting burst
    output back to Redis.

    Parameters
    ------------
    name : str
        The qUnit name
    model : qrobot.models.Model
        The model the qUnit implements
    burst : qrobot.bursts.Burst
        The burst the qUnit implements
    sampling_period : float
        The sampling time with wich the qUnit reads the input
    query : list, optional
        The target state for the model queries. Defaults to ``None``
    in_units : dict[int, str], optional
        Dictionary containing {``dim`` : ``qunit_id``} inputs
        couplings, i.e. ``qunit_id`` output is the input for dimension
        ``dim``. Defaults to ``None``.
    default_input: List[float]
        Default input vector of scalar values to use as default value
        when qunit does not have an available one.
        Defaults to ``model.n*[0.0]``

    Attributes
    ----------
    id : str
        The unique instance identifier of the qUnit
    name : str
        The unique instance identifier of the qUnit
    model : qrobot.models.Model
        The model which the qUnit implements
    burst : qrobot.bursts.Burst
        The burst the qUnit implements
    sampling_period : float
        The sampling period for which the qUnit samples an event
    default_input: List[float]
        Default input vector of scalar values to use as default value
        when qunit does not have an available one
    """

    def __init__(
        self,
        name: str,
        model: Model,
        burst: Burst,
        sampling_period: float | int,
        query: list[float] | None = None,
        in_qunits: dict[int, str] | None = None,
        default_input: list[float] | None = None,
        redis_config: RedisConfig | None = None,
        logging_config: LoggingConfig | None = None,
    ) -> None:
        # Call the BaseUnit constructor
        super().__init__(name, sampling_period, redis_config, logging_config)

        # Store the qUnits name and properties
        self.model = model
        self.burst = burst
        self.default_input = self.model._target_vector_check(
            default_input if default_input is not None else [0.0] * model.n
        )

        # Default query to all 0s if not specified
        query = self.model._target_vector_check(
            query if query is not None else [0.0] * self.model.n
        )

        # Initialize multiprocessing variables
        # - Query array variable
        self._query = self._multiproc_manager.list(query)
        # - Output unit dictionary
        self._in_qunits = self._multiproc_manager.dict(in_qunits or {})
        # - Time window index
        self._t_idx = self._multiproc_manager.Value("i", 0)

        # Log properties
        self._logger.debug(f"Properties: {self}")

    def __iter__(self) -> Generator[tuple[str, object], None, None]:
        yield "name", self.name
        yield "id", self.id
        yield "model", str(self.model)
        yield "burst", str(self.burst.__class__)
        yield "query", self.query
        yield "sampling_period", self.sampling_period

    @property
    def query(self) -> list[float]:
        """Current target state for the model queries

        Returns
        -------
        list
            The query target state array in the computational basis
        """
        return list(self._query)

    @query.setter
    def query(self, query: list[float]) -> None:
        """Set a new query state for the qunit

        Parameters
        -----------
        query : list
            The query target state array in the computational basis
        """
        # Check arguments
        query = self.model._target_vector_check(query)
        # Update accumulator
        self._logger.debug(f"Changing query from {self._query} to {query}")
        for idx, value in enumerate(query):
            self._query[idx] = value
        self._logger.debug(f"_query={self._query}")

    @property
    def in_qunits(self) -> dict[int, str | None]:
        """Current output ``{dim : qunit_id}`` couplings.

        Returns
        -------
        dict
            The current output ``{dim : qunit_id}`` couplings dictionary
        """
        in_qunits: dict[int, str | None] = {}
        for dim in range(self.model.n):
            try:
                in_qunits[dim] = self._in_qunits[dim]
            except KeyError:
                in_qunits[dim] = None
        return in_qunits

    @property
    def input_vector(self) -> list[float]:
        """The current input vector of the unit

        Returns
        -------
        list
            The current input vector
        """
        # Inputs received from Redis must not alter the configured fallback
        # values used by later temporal windows.
        input_vector = self.default_input.copy()
        for dim, qunit_id in self._in_qunits.items():
            _r = redis_utils.get_redis(self.redis_config)
            val = _r.get(qunit_id + " output")
            if val is not None:
                input_vector[dim] = float(val)
            else:
                self._logger.info(f"Unable to read {qunit_id} input")
        return input_vector

    def set_input(self, dim: int, qunit_id: str) -> None:
        """Set a new input qunit for the desired dimension

        Parameters
        -----------
        dim : int
            The input dimension index
        qunit_id : str
            The input qunit id
        """
        # Check arguments
        dim = self.model._dim_index_check(dim)
        # Update accumulator
        self._logger.debug(
            f"Changing dim {dim} input from " + f"{self.in_qunits[dim]} to {qunit_id}"
        )
        self._in_qunits[dim] = qunit_id
        self._logger.debug(f"_in_qunits={self._in_qunits}")

    def get_burst_output(self) -> float | None:
        """Get the latest burst output from the qUnit

        Returns
        -------
        float
            The latest burst output written by the unit on the Redis database
        """
        global_status = redis_utils.redis_status(self.redis_config)
        out = global_status.get(f"{self.id} output", None)
        return float(out) if out is not None else None

    def _clean_redis(self) -> None:
        """Clean all the redis entries created by the unit when the loop stops."""
        _r = redis_utils.get_redis(self.redis_config)
        _r.delete(self.id + " output")
        _r.delete(self.id + " state")
        _r.delete(self.id + " query")
        _r.delete(self.id + " in_qunits")

    def _unit_task(self) -> None:
        """Single iteration of the processing loop."""
        # "_t_idx" is the event index of the temporal window
        self._logger.debug(f"Temporal window event {self._t_idx.value + 1}/{self.model.tau}")
        # Get input
        input_vector = self.input_vector
        self._logger.debug(f"input_vector={input_vector}")
        # Loop through the dimensions to encode data
        for dim in range(self.model.n):
            self.model.encode(input_vector[dim], dim)
        # Wait for the next input in the time window
        self._t_idx.value += 1
        # If at the end of the time window
        if self._t_idx.value == self.model.tau:
            # Apply the query
            self._logger.debug(f"Querying for state {self._query}")
            self.model.query(self.query)
            # Decode
            out_state = self.model.decode()
            self._logger.debug(f"Output state = {out_state}")
            # Write output on Redis database
            self._logger.debug("Opening a connection to redis...")
            _r = redis_utils.get_redis(self.redis_config)
            self._logger.debug(f"Redis connected: {_r}")
            try:
                written = _r.mset(
                    {
                        self.id + " output": self.burst(out_state),
                        self.id + " state": str(out_state),
                        self.id + " query": json.dumps(self.query),
                        self.id + " in_qunits": json.dumps(self.in_qunits),
                    }
                )
            except redis.RedisError as exc:
                raise RedisWriteError(f"Unable to write qUnit {self.id} state to Redis") from exc
            if not written:
                raise RedisWriteError(f"Redis did not write qUnit {self.id} state")
            # Initialize new temporal window
            self._logger.debug("Initializing a new temporal window")
            self.model.clear()
            self._t_idx.value = 0
