import json
from typing import Dict, List

from ..bursts import Burst
from ..models import Model
from . import redis_utils
from .base import BaseUnit


class QUnit(BaseUnit):  # pylint: disable=too-many-instance-attributes
    """[QUnit description]

    Parameters
    ------------
    name : str
        The qUnit name
    model : qrobot.models.Model
        The model the qUnit implements
    burst : qrobot.bursts.Burst
        The burst the qUnit implements
    Ts : float
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
    Ts : float
        The sampling period for which the qUnit samples an event
    default_input: List[float]
        Default input vector of scalar values to use as default value
        when qunit does not have an available one
    """

    def __init__(  # pylint: disable=too-many-arguments
        self,
        name: str,
        model: Model,
        burst: Burst,
        Ts: float,  # pylint: disable=invalid-name
        query: list = None,
        in_qunits: Dict[int, str] = None,
        default_input: float = None,
    ) -> None:
        # Call the BaseUnit constructor
        super().__init__(name, Ts)

        # Store the qUnits name and properties
        self.model = model
        self.burst = burst
        self.default_input = default_input or model.n * [0.0]

        # Default query to all 0s if not specified
        if query is None:
            query = [0.0] * (self.model.n)

        # Initialize multiprocessing variables
        # - Query array variable
        self._query = self._multiproc_manager.list(query)
        # - Output unit dictionary
        self._in_qunits = self._multiproc_manager.dict(in_qunits or {})
        # - Time window index
        self._t_idx = self._multiproc_manager.Value("i", 0)

        # Log properties
        self._logger.debug(f"Properties: {self}")

    def __iter__(self):
        yield "name", self.name
        yield "id", self.id
        yield "model", str(self.model)
        yield "burst", str(self.burst.__class__)
        yield "query", self.query
        yield "Ts", self.Ts

    @property
    def query(self) -> List[float]:
        """Current target state for the model queries

        Returns
        -------
        list
            The query target state array in the computational basis
        """
        return list(self._query)

    @query.setter
    def query(self, query: list) -> None:
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
    def in_qunits(self) -> Dict[int, str]:
        """Current output ``{dim : qunit_id}`` couplings.

        Returns
        -------
        dict
            The current output ``{dim : qunit_id}`` couplings dictionary
        """
        in_qunits = {}
        for dim in range(self.model.n):
            try:
                in_qunits[dim] = self._in_qunits[dim]
            except KeyError:
                in_qunits[dim] = None
        return in_qunits

    @property
    def input_vector(self) -> List[float]:
        """The current input vector of the unit

        Returns
        -------
        list
            The current input vector
        """
        input_vector = self.default_input
        for dim, qunit_id in self._in_qunits.items():
            _r = redis_utils.get_redis()
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
        dim = self.model._dim_index_check(dim)  # pylint: disable=protected-access
        # Update accumulator
        self._logger.debug(
            f"Changing dim {dim} input from " + f"{self.in_qunits[dim]} to {qunit_id}"
        )
        self._in_qunits[dim] = qunit_id
        self._logger.debug(f"_in_qunits={self._in_qunits}")

    def _clean_redis(self) -> None:
        """Clean all the redis entries created by the unit when the loop stops."""
        _r = redis_utils.get_redis()
        _r.delete(self.id + " output")
        _r.delete(self.id + " state")
        _r.delete(self.id + " query")
        _r.delete(self.id + " in_qunits")

    def _unit_task(self) -> None:
        """Single iteration of the processing loop."""
        # "_t_idx" is the event index of the temporal window
        self._logger.debug(
            f"Temporal window event {self._t_idx.value+1}/{self.model.tau}"
        )
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
            _r = redis_utils.get_redis()
            self._logger.debug(f"Redis connected: {_r}")
            if not (
                _r.mset({self.id + " output": self.burst(out_state)})
                and _r.mset({self.id + " state": str(out_state)})
                and _r.mset({self.id + " query": json.dumps(self.query)})
                and _r.mset({self.id + " in_qunits": json.dumps(self.in_qunits)})
            ):
                raise Exception(
                    f"Problem in writing qunit {self.id} output on Redis database!"
                )
            # Initialize new temporal window
            self._logger.debug("Initializing a new temporal window")
            self.model.clear()
            self._t_idx.value = 0
