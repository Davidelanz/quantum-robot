from . import redis_utils
from .base import BaseUnit
from .redis_utils import RedisConfig, RedisWriteError
from qrobot.logger import LoggingConfig
import redis
from collections.abc import Generator


class SensorialUnit(BaseUnit):  # pylint: disable=too-many-instance-attributes
    """Unit periodically sending normalized scalar readings.

    Parameters
    ------------
    name : str
        The SensorialUnit name
    Ts : float
        The sampling time with wich the SensorialUnit reads the input
    default_input: float
        Default input for the scalar readings when the SensorialUnit
        does not have an available one. Defaults to 0

    Attributes
    ----------
    id : str
        The unique instance identifier of the SensorialUnit
    name : str
        The unique instance identifier of the SensorialUnit
    Ts : float
        The sampling period for which the SensorialUnit samples an event
    default_input: float
        Default input for the scalar readings when the SensorialUnit
        does not have an available one
    """

    def __init__(  # pylint: disable=too-many-arguments
        self,
        name: str,
        Ts: float | int,  # pylint: disable=invalid-name
        default_input: float | None = None,
        redis_config: RedisConfig | None = None,
        logging_config: LoggingConfig | None = None,
    ) -> None:
        # Call the BaseUnit constructor
        super().__init__(name, Ts, redis_config, logging_config)

        # Store the SensorialUnit name and properties
        self.default_input = 0.0 if default_input is None else default_input

        # Initialize multiprocessing variables
        # - _scalar_reading array variable
        self._scalar_reading = self._multiproc_manager.Value("d", self.default_input)

        # Log properties
        self._logger.debug(f"Properties: {self}")

    def __iter__(self) -> Generator[tuple[str, object], None, None]:
        yield "name", self.name
        yield "id", self.id
        yield "Ts", self.Ts

    @property
    def scalar_reading(self) -> float:
        """Current scalar reading."""
        return self._scalar_reading.value

    @scalar_reading.setter
    def scalar_reading(self, value: float) -> None:
        """Set a new value for the input"""
        # Update accumulator
        self._logger.debug(
            f"Changing scalar reading from {self._scalar_reading.value} to {value}"
        )
        self._scalar_reading.value = value
        self._logger.debug(f"_scalar_reading={self._scalar_reading.value}")

    def _clean_redis(self) -> None:
        """Clean all the redis entries created by the unit when the loop stops."""
        _r = redis_utils.get_redis(self.redis_config)
        _r.delete(self.id + " output")

    def _unit_task(self) -> None:
        """Single iteration of the processing loop."""
        # Get reading
        scalar_reading = self.scalar_reading
        self._logger.debug(f"scalar_reading={scalar_reading}")
        self._logger.debug("Writing input on redis")
        # Write it on redis
        _r = redis_utils.get_redis(self.redis_config)
        try:
            written = _r.mset({self.id + " output": self.scalar_reading})
        except redis.RedisError as exc:
            raise RedisWriteError(
                f"Unable to write SensorialUnit {self.id} output to Redis"
            ) from exc
        if not written:
            raise RedisWriteError(f"Redis did not write SensorialUnit {self.id} output")
