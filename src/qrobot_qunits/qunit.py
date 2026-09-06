"""Redis-connected quantum-like processing unit."""

import json
import logging
from collections.abc import Generator

import redis

from qrobot.bursts import Burst
from qrobot.logger import LoggingConfig
from qrobot.models import Model
from .redis import RedisAttribute, build_redis_key
from .redis import read_outputs
from .base import BaseUnit
from .redis import RedisConfig, RedisWriteError


class QUnit(BaseUnit):
    """Periodically process coupled inputs through a quantum-like model.

    A qUnit reads its inputs from Redis, encodes them over the model's
    temporal window, applies a query, and publishes the resulting burst
    output back to Redis.

    Parameters
    ----------
    name : str
        Human-readable qUnit name.
    model : qrobot.models.Model
        Quantum-like model used to encode each temporal window.
    burst : qrobot.bursts.Burst
        Rule that converts a decoded state to a normalized output.
    sampling_period : float
        Seconds between input samples.
    query : list, optional
        Query target with one value per model dimension. Defaults to the
        all-zero vector.
    in_qunits : dict[int, str], optional
        Mapping from model dimensions to upstream unit IDs. Each mapped unit's
        Redis output supplies that dimension.
    default_input: List[float]
        Default input vector of scalar values to use as default value
        when qUnit does not have an available one.
        Defaults to one zero per model dimension.

    Attributes
    ----------
    id : str
        Unique qUnit instance identifier.
    name : str
        Human-readable qUnit name.
    model : qrobot.models.Model
        Model used to encode temporal windows.
    burst : qrobot.bursts.Burst
        Rule used to convert decoded states to outputs.
    sampling_period : float
        Seconds between input samples.
    default_input : list[float]
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
        self._query = self._shared_list(query)
        # - Output unit dictionary
        self._in_qunits = self._shared_dict(in_qunits or {})
        # - Time window index
        self._t_idx = self._shared_value("i", 0)

        # Log properties
        self._logger.debug("Properties: %s", self)

    def __iter__(self) -> Generator[tuple[str, object], None, None]:
        """Yield the qUnit configuration as key-value pairs."""
        yield "name", self.name
        yield "id", self.id
        yield "model", str(self.model)
        yield "burst", str(self.burst.__class__)
        yield "query", self.query
        yield "sampling_period", self.sampling_period

    @property
    def query(self) -> list[float]:
        """Return the current query target.

        Returns
        -------
        list
            Normalized target value for each model dimension.
        """
        return list(self._query)

    @query.setter
    def query(self, query: list[float]) -> None:
        """Set the query target used at the end of each temporal window.

        Parameters
        ----------
        query : list
            Normalized target value for each model dimension.
        """
        # Check arguments
        query = self.model._target_vector_check(query)
        # Update accumulator
        if self._logger.isEnabledFor(logging.DEBUG):
            self._logger.debug("Changing query from %s to %s", self._query, query)
        for idx, value in enumerate(query):
            self._query[idx] = value
        if self._logger.isEnabledFor(logging.DEBUG):
            self._logger.debug("_query=%s", self._query)

    @property
    def in_qunits(self) -> dict[int, str | None]:
        """Return input unit IDs indexed by model dimension.

        Returns
        -------
        dict
            Complete dimension mapping; unconnected dimensions map to ``None``.
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
        """Read the current input vector from input Redis outputs.

        Returns
        -------
        list
            One normalized value per model dimension. Missing input outputs
            use the corresponding ``default_input`` value.
        """
        # Inputs received from Redis must not alter the configured fallback
        # values used by later temporal windows.
        input_vector = self.default_input.copy()
        inputs = list(self._in_qunits.items())
        values = read_outputs(self._redis(), (unit_id for _, unit_id in inputs))
        for (dim, unit_id), value in zip(inputs, values):
            if value is not None:
                input_vector[dim] = self._normalize_input(dim, value)
            else:
                self._logger.info("Unable to read %s input", unit_id)
        return input_vector

    def _normalize_input(self, dim: int, value: object) -> float:
        """Return a normalized Redis input, falling back when invalid."""
        try:
            normalized = float(value)  # type: ignore[arg-type]
        except (TypeError, ValueError):
            normalized = self.default_input[dim]
        if not 0.0 <= normalized <= 1.0:
            normalized = self.default_input[dim]
        return normalized

    def set_input(self, dim: int, input_id: str) -> None:
        """Connect a new input to the specified dimension to the qUnit.

        Parameters
        ----------
        dim : int
            The input dimension index
        input_id : str
            The new input unit ID
        """
        # Check arguments
        dim = self.model._dim_index_check(dim)
        # Update accumulator
        if self._logger.isEnabledFor(logging.DEBUG):
            self._logger.debug(
                "Changing dim %s input from %s to %s",
                dim,
                self.in_qunits[dim],
                input_id,
            )
        self._in_qunits[dim] = input_id
        if self._logger.isEnabledFor(logging.DEBUG):
            self._logger.debug("_in_qunits=%s", self._in_qunits)

    def _initial_redis_state(self) -> dict[str, str | int | float]:
        """Return qUnit type, query, and input topology available at startup."""
        return {
            **super()._initial_redis_state(),
            build_redis_key(self.id, RedisAttribute.QUERY): json.dumps(self.query),
            build_redis_key(self.id, RedisAttribute.IN_QUNITS): json.dumps(self.in_qunits),
        }

    def get_burst_output(self) -> float | None:
        """Return the latest burst output published by the qUnit.

        Returns
        -------
        float or None
            The latest burst output written by the unit on the Redis database.
        """
        client = self._redis()
        output = client.get(build_redis_key(self.id, RedisAttribute.OUTPUT))
        return float(output) if output is not None else None

    def _clean_redis(self) -> None:
        """Clean all the redis entries created by the unit when the loop stops."""
        _r = self._redis()
        _r.delete(
            build_redis_key(self.id, RedisAttribute.OUTPUT),
            build_redis_key(self.id, RedisAttribute.STATE),
            build_redis_key(self.id, RedisAttribute.QUERY),
            build_redis_key(self.id, RedisAttribute.IN_QUNITS),
        )

    def _unit_task(self) -> None:
        """Single iteration of the processing loop."""
        # "_t_idx" is the event index of the temporal window
        if self._logger.isEnabledFor(logging.DEBUG):
            self._logger.debug(
                "Temporal window event %s/%s",
                self._t_idx.value + 1,
                self.model.tau,
            )
        # Get input
        input_vector = self.input_vector
        if self._logger.isEnabledFor(logging.DEBUG):
            self._logger.debug("input_vector=%s", input_vector)
        self.model.encode_vector(input_vector)
        # Wait for the next input in the time window
        self._t_idx.value += 1
        # If at the end of the time window
        if self._t_idx.value == self.model.tau:
            # Apply the query
            if self._logger.isEnabledFor(logging.DEBUG):
                self._logger.debug("Querying for state %s", self._query)
            self.model.query(self.query)
            # Decode
            out_state = self.model.decode()
            if self._logger.isEnabledFor(logging.DEBUG):
                self._logger.debug("Output state = %s", out_state)
            # Write output on Redis database
            if self._logger.isEnabledFor(logging.DEBUG):
                self._logger.debug("Opening a connection to redis...")
            _r = self._redis()
            if self._logger.isEnabledFor(logging.DEBUG):
                self._logger.debug("Redis connected: %s", _r)
            try:
                written = self._write_changed_redis_state(
                    {
                        build_redis_key(self.id, RedisAttribute.OUTPUT): self.burst(out_state),
                        build_redis_key(self.id, RedisAttribute.STATE): str(out_state),
                        build_redis_key(self.id, RedisAttribute.QUERY): json.dumps(self.query),
                        build_redis_key(self.id, RedisAttribute.IN_QUNITS): json.dumps(
                            self.in_qunits
                        ),
                    }
                )
            except redis.RedisError as exc:
                raise RedisWriteError(f"Unable to write qUnit {self.id} state to Redis") from exc
            if not written:
                raise RedisWriteError(f"Redis did not write qUnit {self.id} state")
            # Initialize new temporal window
            if self._logger.isEnabledFor(logging.DEBUG):
                self._logger.debug("Initializing a new temporal window")
            self.model.clear()
            self._t_idx.value = 0
