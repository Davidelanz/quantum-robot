"""Shared lifecycle for periodically scheduled Redis-connected units."""

import multiprocessing
from abc import ABC, abstractmethod
from collections.abc import Generator
from multiprocessing.managers import SyncManager
from time import monotonic
from typing import Any
from uuid import uuid4

import redis

from qrobot.logger import LoggingConfig, configure_logging, get_logger
from .redis import RedisAttribute, build_redis_key
from .redis import get_redis
from .redis import RedisConfig

MIN_TS = 0.01
"""Minimum supported sampling period, in seconds."""

STOP_TIMEOUT = 5.0
"""Seconds to wait for a worker to stop before terminating it."""


class BaseUnit(ABC):
    """Base class for periodically scheduled, Redis-connected units.

    Each unit runs ``_unit_task`` in a child process at ``sampling_period``
    intervals and publishes its externally visible state under its unique ID.

    Parameters
    ----------
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
        self._worker_redis: redis.Redis | None = None
        # Managed containers are created lazily because most unit types only
        # need lightweight shared values.
        self._multiproc_manager: SyncManager | None = None

        # Used to gracefully stop the worker letting it finish its current task.
        self._stop_event = multiprocessing.Event()

        # A process is deliberately created when ``start`` is called. On
        # platforms using the ``spawn`` start method, creating it while the
        # object is still being initialized captures the manager's own worker
        # process and makes the unit impossible to pickle.
        self._loop_thread: multiprocessing.Process | None = None

    def __getstate__(self) -> dict[str, Any]:
        """Serialize process-safe state without local runtime handles."""
        state = self.__dict__.copy()
        state["_multiproc_manager"] = None
        state["_loop_thread"] = None
        state["_worker_redis"] = None
        return state

    def __iter__(self) -> Generator[tuple[str, object], None, None]:
        """Yield the unit configuration as key-value pairs."""
        yield "name", self.name
        yield "id", self.id
        yield "sampling_period", self.sampling_period

    def __repr__(self) -> str:
        """Return the unit identifier and configuration."""
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
        self._stop_event.clear()
        self._loop_thread = multiprocessing.Process(target=self._loop)
        self._loop_thread.start()
        # Add the unit with its class to redis
        _r = get_redis(self.redis_config)
        _r.mset({build_redis_key(self.id, RedisAttribute.CLASS): self.__class__.__name__})

    def stop(self, timeout: float = STOP_TIMEOUT) -> None:
        """Stop the worker and delete its Redis keys.

        The worker finishes its current task before exiting. If it does not
        exit within ``timeout`` seconds, it is terminated as a last resort.
        Redis keys owned by the unit are removed after either a graceful or
        forced exit.

        Parameters
        ----------
        timeout : float
            Seconds to wait for a graceful exit before forcing termination.
        """
        if timeout < 0:
            raise ValueError("timeout must not be negative")
        if self._loop_thread is None:
            self._logger.warning(f"{self.__class__.__name__} is not running")
            return
        self._logger.info(f"Stopping {self.__class__.__name__}")
        self._stop_event.set()
        self._loop_thread.join(timeout)
        if self._loop_thread.is_alive():
            self._logger.warning(
                f"{self.__class__.__name__} did not stop within {timeout} seconds; terminating"
            )
            self._loop_thread.terminate()
            self._loop_thread.join()
        self._loop_thread = None
        self._logger.info("Cleaning redis")
        self._clean_redis()
        # Remove the unit with its class from redis
        _r = get_redis(self.redis_config)
        _r.delete(build_redis_key(self.id, RedisAttribute.CLASS))

    @abstractmethod
    def _clean_redis(self) -> None:
        """Clean all the redis entries created by the unit when the loop stops."""
        raise NotImplementedError

    @abstractmethod
    def _unit_task(self) -> None:
        """Task executed by the unit every sampling period."""
        raise NotImplementedError

    def _loop(self) -> None:
        if self.logging_config is not None:
            configure_logging(self.logging_config)
        self._worker_redis = get_redis(self.redis_config)
        deadline = monotonic()
        try:
            while not self._stop_event.is_set():
                self._unit_task()
                deadline += self.sampling_period
                now = monotonic()
                if now >= deadline:
                    missed_periods = int((now - deadline) // self.sampling_period) + 1
                    deadline += missed_periods * self.sampling_period
                self._stop_event.wait(deadline - now)
        finally:
            self._worker_redis.close()
            self._worker_redis = None

    def _redis(self) -> redis.Redis:
        """Return the worker's Redis client or a client for a parent-side call."""
        return getattr(self, "_worker_redis", None) or get_redis(self.redis_config)

    def _shared_value(self, typecode: str, value: int | float) -> Any:
        """Create a process-safe scalar without starting a manager process."""
        return multiprocessing.Value(typecode, value)

    def _shared_list(self, values: list[Any]) -> Any:
        """Create a managed list shared with the unit's worker process."""
        return self._manager().list(values)

    def _shared_dict(self, values: dict[Any, Any]) -> Any:
        """Create a managed dictionary shared with the unit's worker process."""
        return self._manager().dict(values)

    def _manager(self) -> SyncManager:
        """Return this unit's manager, creating it only when first required."""
        if self._multiproc_manager is None:
            self._multiproc_manager = multiprocessing.Manager()
        return self._multiproc_manager

    @staticmethod
    def _period_check(sampling_period: float | int) -> float:
        """Ensure a sampling period is a number above the minimum allowed.

        Raises
        ------
        TypeError:
            ``sampling_period`` is not an ``int`` or ``float``.
        ValueError
            ``sampling_period`` must not be lower than the minimum allowed.

        Returns
        -------
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
