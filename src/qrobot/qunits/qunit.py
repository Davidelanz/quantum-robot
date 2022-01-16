import multiprocessing
from time import sleep
from typing import Dict, List
from uuid import uuid4

import redis

from ..bursts import Burst
from ..logs import get_logger
from ..models import Model

MIN_TS = 0.01
""" float: Minimum sampling period allowed (in seconds).
"""


def _get_redis(host="localhost", port=6379, db=0):
    return redis.Redis(host, port, db)


def redis_status() -> dict:
    """Returns the current redis database status in the for of a dictionary
    with {db_key : db_value} mapping.

    Returns:
        dict: Redis current status
    """
    _r = _get_redis()
    status = {}
    for key in _r.scan_iter():
        status[key.decode("ascii")] = _r.get(key).decode("ascii")
    return status


def flush_redis() -> None:
    """Flush the redis database"""
    logger = get_logger("redis")
    logger.info("Flushing redis database")
    logger.debug(f"Previous redis state: {redis_status()}")
    _r = _get_redis()
    _r.flushdb()
    logger.debug(f"Current redis state: {redis_status()}")


class QUnit:
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
    default_input: float
        Default scalar input value when qunit does not have an available one.
        Defaults to 0.0

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
    default_input: float
        Default scalar input value when qunit does not have an available one.
        Defaults to 0.0
    """

    # ========================================================
    # CONSTRUCTOR
    # ========================================================

    def __init__(
        self,
        name: str,
        model: Model,
        burst: Burst,
        Ts: float,
        query: list = None,
        in_qunits: Dict[int, str] = None,
        default_input: float = 0.0,
    ) -> None:
        # Create a instance unique identifier
        self.id = name + "-" + str(uuid4())[:6]
        # use it for log
        self._logger = get_logger(self.id)
        self._logger.debug(f"Initializing qUnit {self.id}")

        # Store the qUnits name and properties
        self.name = name
        self.model = model
        self.burst = burst
        self.Ts = self._period_check(Ts)
        self.default_input = default_input

        if query is None:
            query = [0.0] * (self.model.n)

        # Initialize multiprocessing variables
        # (common to all threads while being modified)
        manager = multiprocessing.Manager()
        # Query array variable
        self._query = manager.list(query)
        # Output unit dictionary
        self._in_qunits = manager.dict(in_qunits or {})

        # Log properties
        self._logger.debug(f"Properties: {self}")

        # Initialize threads
        self._loop_thread = multiprocessing.Process(target=self._loop)

    # ========================================================
    # PROPERTIES
    # ========================================================

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
        for i, q in enumerate(query):
            self._query[i] = q
        self._logger.debug(f"_query={self._query}")

    @property
    def in_qunits(self) -> Dict[int, str]:
        """Current output {``dim`` : ``qunit_id``} couplings

        Returns
        -------
        dict
            The current output {``dim`` : ``qunit_id``} couplings dictionary
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
        input_vector = [self.default_input] * self.model.n
        for dim, qunit_id in self._in_qunits.items():
            _r = _get_redis()
            val = _r.get(qunit_id)
            if val is not None:
                input_vector[dim] = float(val)
            else:
                self._logger.info(f"Unable to read {qunit_id} input")
                input_vector[dim] = self.default_input
        return input_vector

    # ========================================================
    # BUILT-IN
    # ========================================================

    def __iter__(self):
        yield "name", self.name
        yield "id", self.id
        yield "model", str(self.model)
        yield "burst", str(self.burst.__class__)
        yield "query", self.query
        yield "Ts", self.Ts

    def __repr__(self) -> str:
        out_str = f'QUnit "{self.id}"'
        for k, v in dict(self).items():
            out_str += f"\n     {k}:\t{v}"
        return out_str

    # ========================================================
    # METHODS
    # ========================================================

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

    def start(self) -> None:
        """Starts the qUnit background threads"""
        try:
            self._loop_thread.start()
            self._logger.info("Starting qUnit")
        except AssertionError:
            self._logger.warning("qUnit is already started")

    def stop(self) -> None:
        """Stops the qUnit background threads"""
        try:
            self._loop_thread.terminate()
            self._logger.info("Stopping qUnit")
        except AssertionError:
            self._logger.warning("qUnit is not running")
        # Delete outputs from redis
        _r = _get_redis()
        _r.delete(self.id)
        _r.delete(self.id + " state")

    # ========================================================
    # PRIVATE METHODS
    # ========================================================

    @staticmethod
    def _period_check(Ts) -> float:
        """This method ensures that a `Ts` for the qUnit
        is an integer or a float greater than the minimum allowed.

        Raises
        ---------
        TypeError:
            `Ts` is nor a `int` or a `float`
        ValueError
            `Ts` must not be lower than Core's global update period

        Returns
        --------
        float
            The `Ts`
        """
        if not isinstance(Ts, (float, int)):
            raise TypeError(f"Ts must be an scalar number, not a {type(Ts)}!")
        if Ts < MIN_TS:
            raise ValueError(f"Ts must not be lower than {MIN_TS}!")
        return float(Ts)

    # ========================================================
    # THREADS
    # ========================================================

    def _loop(self) -> None:
        while True:

            self._logger.debug("Initializing a new temporal window")
            self.model.clear()
            # "t" is the event index of the temporal window
            for t in range(self.model.tau):

                self._logger.debug(f"Temporal window event {t+1}/{self.model.tau}")

                # Get input
                input_vector = self.input_vector
                self._logger.debug(f"input_vector={input_vector}")

                # Loop through the dimensions to encode data
                for dim in range(self.model.n):
                    self.model.encode(input_vector[dim], dim)

                # wait for the next input in the time window
                sleep(self.Ts)

            # After the time window, apply the query
            self._logger.debug(f"Querying for state {self._query}")
            self.model.query(self._query)

            # Decode
            out_state = self.model.decode()

            # Write output on Redis database
            self._logger.debug("Writing output on redis")
            _r = _get_redis()
            if not (
                _r.mset({self.id + " state": out_state})
                and _r.mset({self.id: self.burst(out_state)})
            ):
                raise Exception(
                    f"Problem in writing qunit {self.id} " + "output on Redis database!"
                )
