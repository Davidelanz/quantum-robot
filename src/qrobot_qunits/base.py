import multiprocessing
from abc import ABC, abstractmethod
from time import sleep
from uuid import uuid4

from qrobot.logger.logger import get_logger
from . import redis_utils

MIN_TS = 0.01
""" float: Minimum time period allowed (in seconds).
"""


class BaseUnit(ABC):
    """Base abstract class defining the multithreading and redis
    festures implemented by all the units.

    Parameters
    ------------
    name : str
        The unit name
    Ts : float
        The time period with wich the unit execute its task

    Attributes
    ----------
    id : str
        The unique instance identifier of the unit
    name : str
        The unique instance identifier of the unit
    Ts : float
        The time period for which the unit execute its task
    """

    def __init__(  # pylint: disable=too-many-arguments
        self,
        name: str,
        Ts: float,  # pylint: disable=invalid-name
    ) -> None:
        # Create a instance unique identifier
        self.id = name + "-" + str(uuid4())[:6]  # pylint: disable=invalid-name
        # use it for logging purposes
        self._logger = get_logger(self.id)
        self._logger.debug(f"Initializing {self.__class__.__name__} {self.id}")

        # Store the unit name and properties
        self.name = name
        self.Ts = self._period_check(Ts)  # pylint: disable=invalid-name

        # Initialize multiprocessing manager
        self._multiproc_manager = multiprocessing.Manager()
        # To define managed variables:
        # -> self.name = self._multiproc_manager.list(value)

        # A process is deliberately created when ``start`` is called. On
        # platforms using the ``spawn`` start method, creating it while the
        # object is still being initialized captures the manager's own worker
        # process and makes the unit impossible to pickle.
        self._loop_thread: multiprocessing.Process | None = None

    def __getstate__(self):
        """Serialize manager proxies, but not their local manager process."""
        state = self.__dict__.copy()
        state["_multiproc_manager"] = None
        state["_loop_thread"] = None
        return state

    def __iter__(self):
        yield "name", self.name
        yield "id", self.id
        yield "Ts", self.Ts

    def __repr__(self) -> str:
        out_str = f'{self.__class__.__name__} "{self.id}"'
        for key, value in dict(self).items():
            out_str += f"\n     {key}:\t{value}"
        return out_str

    def start(self) -> None:
        """Starts the unit's background threads"""
        if self._loop_thread is not None and self._loop_thread.is_alive():
            self._logger.warning(f"{self.__class__.__name__} is already started")
            return
        self._logger.info(f"Starting {self.__class__.__name__}")
        self._loop_thread = multiprocessing.Process(target=self._loop)
        self._loop_thread.start()
        # Add the unit with its class to redis
        _r = redis_utils.get_redis()
        _r.mset({self.id + " class": self.__class__.__name__})

    def stop(self) -> None:
        """Stops the unit's background threads"""
        if self._loop_thread is None or not self._loop_thread.is_alive():
            self._logger.warning(f"{self.__class__.__name__} is not running")
            return
        self._logger.info(f"Stopping {self.__class__.__name__}")
        self._loop_thread.terminate()
        self._loop_thread.join()
        self._loop_thread = None
        self._logger.info("Cleaning redis")
        self._clean_redis()
        # Remove the unit with its class from redis
        _r = redis_utils.get_redis()
        _r.delete(self.id + " class")

    @abstractmethod
    def _clean_redis(self) -> None:
        """Clean all the redis entries created by the unit when the loop stops."""

    @abstractmethod
    def _unit_task(self) -> None:
        """Task executed by the unit every TS time period."""

    def _loop(self) -> None:
        while True:
            self._unit_task()
            sleep(self.Ts)

    @staticmethod
    def _period_check(Ts) -> float:  # pylint: disable=invalid-name
        """This method ensures that a `Ts` for the unit
        is an integer or a float greater than the minimum allowed.

        Raises
        ---------
        TypeError:
            `Ts` is nor a `int` or a `float`
        ValueError
            `Ts` must not be lower than the minimum allowed

        Returns
        --------
        float
            The time period `Ts`
        """
        if not isinstance(Ts, (float, int)):
            raise TypeError(f"Ts must be an scalar number, not a {type(Ts)}!")
        if Ts < MIN_TS:
            raise ValueError(f"Ts must not be lower than {MIN_TS}!")
        return float(Ts)
