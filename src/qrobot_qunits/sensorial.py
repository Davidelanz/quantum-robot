"""Redis-connected normalized sensor interface."""

from .base import BaseUnit
from .redis import RedisConfig, RedisWriteError
from qrobot.logger import LoggingConfig
from .redis import RedisAttribute, build_redis_key
import redis
from collections.abc import Generator


class SensorialUnit(BaseUnit):
    """Unit periodically sending normalized scalar readings.

    Parameters
    ----------
    name : str
        Human-readable sensor name.
    sampling_period : float
        Seconds between Redis publications.
    default_input: float
        Initial scalar reading. Defaults to ``0.0``.

    Attributes
    ----------
    id : str
        Unique sensor instance identifier.
    name : str
        Human-readable sensor name.
    sampling_period : float
        Seconds between Redis publications.
    default_input: float
        Default input for the scalar readings when the SensorialUnit
        does not have an available one
    """

    def __init__(
        self,
        name: str,
        sampling_period: float | int,
        default_input: float | None = None,
        redis_config: RedisConfig | None = None,
        logging_config: LoggingConfig | None = None,
    ) -> None:
        # Call the BaseUnit constructor
        super().__init__(name, sampling_period, redis_config, logging_config)

        self.default_input = 0.0
        if default_input is not None:
            self.default_input = self._normalize_input(default_input)

        # The simulation updates this value while the sensor worker publishes it.
        self._scalar_reading = self._shared_value("d", self.default_input)

        # Log properties
        self._logger.debug(f"Properties: {self}")

    def __iter__(self) -> Generator[tuple[str, object], None, None]:
        """Yield the sensorial-unit configuration as key-value pairs."""
        yield "name", self.name
        yield "id", self.id
        yield "sampling_period", self.sampling_period

    @property
    def scalar_reading(self) -> float:
        """Current scalar reading."""
        return float(self._scalar_reading.value)

    @scalar_reading.setter
    def scalar_reading(self, value: float | int) -> None:
        """Set the reading published by subsequent unit tasks."""
        value = self._normalize_input(value)
        self._logger.debug(f"Changing scalar reading from {self._scalar_reading.value} to {value}")
        self._scalar_reading.value = value
        self._logger.debug(f"_scalar_reading={self._scalar_reading.value}")

    def _normalize_input(self, value: object) -> float:
        """Return a normalized reading, falling back when invalid."""
        try:
            normalized = float(value)  # type: ignore[arg-type]
        except (TypeError, ValueError):
            normalized = self.default_input
        if not 0.0 <= normalized <= 1.0:
            normalized = self.default_input
        return normalized

    def _clean_redis(self) -> None:
        """Clean all the redis entries created by the unit when the loop stops."""
        _r = self._redis()
        _r.delete(build_redis_key(self.id, RedisAttribute.OUTPUT))

    def _unit_task(self) -> None:
        """Single iteration of the processing loop."""
        # Get reading
        scalar_reading = self.scalar_reading
        self._logger.debug(f"scalar_reading={scalar_reading}")
        self._logger.debug("Writing input on redis")
        # Write it on redis
        _r = self._redis()
        try:
            written = _r.mset(
                {build_redis_key(self.id, RedisAttribute.OUTPUT): self.scalar_reading}
            )
        except redis.RedisError as exc:
            raise RedisWriteError(
                f"Unable to write SensorialUnit {self.id} output to Redis"
            ) from exc
        if not written:
            raise RedisWriteError(f"Redis did not write SensorialUnit {self.id} output")
