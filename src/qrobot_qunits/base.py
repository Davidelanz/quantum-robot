import multiprocessing
from abc import ABC, abstractmethod
from collections.abc import Generator
from time import sleep
from typing import Any
from uuid import uuid4

from qrobot.logger import LoggingConfig, configure_logging, get_logger
from . import redis_utils
from .redis_utils import RedisConfig

MIN_TS = 0.01
"""Minimum supported sampling period, in seconds."""


class BaseUnit(ABC):
    """Base class for periodically scheduled, Redis-connected units.

    Each unit runs ``_unit_task`` in a child process at ``sampling_period``
    intervals and publishes its externally visible state under its unique ID.

    Parameters
    ------------
    name : str
        Human-readable unit name used as the ID prefix.
    sampling_period : float
        Seconds between task executions. The minimum is :data:`MIN_TS`.

    Attributes
    ----------
    id : str
        Unique instance identifier composed from ``name`` and a random suffix.
    name : str
        Human-readable unit name.
    sampling_period : float
        Seconds between task executions.
    """

    def __init__(
        self,
        name: str,
        sampling_period: float | int,
        redis_config: RedisConfig | None = None,
        logging_config: LoggingConfig | None = None,
    ) -> None:
        # The random suffix lets units with the same display name coexist.
        self.id = name + "-" + str(uuid4())[:6]
        self._logger = get_logger(self.id)
        self._logger.debug(f"Initializing {self.__class__.__name__} {self.id}")

        # Store the unit name and properties
        self.name = name
        self.sampling_period = self._period_check(sampling_period)
        self.redis_config = redis_config or RedisConfig()
        self.logging_config = logging_config

        # Subclasses store state shared with their worker process in this manager.
        self._multiproc_manager = multiprocessing.Manager()
        # To define managed variables:
        # -> self.name = self._multiproc_manager.list(value)

        # A process is deliberately created when ``start`` is called. On
        # platforms using the ``spawn`` start method, creating it while the
        # object is still being initialized captures the manager's own worker
        # process and makes the unit impossible to pickle.
        self._loop_thread: multiprocessing.Process | None = None

    def __getstate__(self) -> dict[str, Any]:
        """Serialize manager proxies, but not their local manager process."""
        state = self.__dict__.copy()
        state["_multiproc_manager"] = None
        state["_loop_thread"] = None
        return state

    def __iter__(self) -> Generator[tuple[str, object], None, None]:
        yield "name", self.name
        yield "id", self.id
        yield "sampling_period", self.sampling_period

    def __repr__(self) -> str:
        out_str = f'{self.__class__.__name__} "{self.id}"'
        for key, value in dict(self).items():
            out_str += f"\n     {key}:\t{value}"
        return out_str

    def start(self) -> None:
        """Start the unit's background process and publish its type."""
        if self._loop_thread is not None and self._loop_thread.is_alive():
            self._logger.warning(f"{self.__class__.__name__} is already started")
            return
        self._logger.info(f"Starting {self.__class__.__name__}")
        self._loop_thread = multiprocessing.Process(target=self._loop)
        self._loop_thread.start()
        # Add the unit with its class to redis
        _r = redis_utils.get_redis(self.redis_config)
        _r.mset({self.id + " class": self.__class__.__name__})

    def stop(self) -> None:
        """Terminate the worker process and delete the unit's Redis keys."""
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
        _r = redis_utils.get_redis(self.redis_config)
        _r.delete(self.id + " class")

    @abstractmethod
    def _clean_redis(self) -> None:
        """Clean all the redis entries created by the unit when the loop stops."""

    @abstractmethod
    def _unit_task(self) -> None:
        """Task executed by the unit every sampling period."""

    def _loop(self) -> None:
        if self.logging_config is not None:
            configure_logging(self.logging_config)
        while True:
            self._unit_task()
            sleep(self.sampling_period)

    @staticmethod
    def _period_check(sampling_period: float | int) -> float:
        """Ensure a sampling period is a number above the minimum allowed.

        Raises
        ---------
        TypeError:
            ``sampling_period`` is not an ``int`` or ``float``.
        ValueError
            ``sampling_period`` must not be lower than the minimum allowed.

        Returns
        --------
        float
            The validated sampling period.
        """
        if not isinstance(sampling_period, (float, int)):
            raise TypeError(
                f"sampling_period must be a scalar number, not a {type(sampling_period)}!"
            )
        if sampling_period < MIN_TS:
            raise ValueError(f"sampling_period must not be lower than {MIN_TS}!")
        return float(sampling_period)
