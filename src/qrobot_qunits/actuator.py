"""Redis-connected actuator interfaces for qBrain networks."""

import json
from collections.abc import Generator

import redis

from qrobot.logger import LoggingConfig
from .redis import RedisAttribute, build_redis_key

from .redis import get_redis
from .base import BaseUnit
from .redis import RedisConfig, RedisWriteError


class ActuatorUnit(BaseUnit):
    """Map the normalized sum of qUnit bursts to behavioral activation.

    This implements the actuator interface: read one or more qUnit bursts,
    average them, and activate a behavioral routine when the normalized sum
    is strictly greater than a configured threshold. The unit's output is
    stored in Redis as ``0.0`` (inhibited) or ``1.0`` (active), so a simulated
    or physical routine can consume it without being coupled to the qUnit worker.

    Parameters
    ----------
    name : str
        The actuator name.
    in_qunits : list[str] | tuple[str, ...]
        Identifiers of the qUnits whose bursts drive the actuator.
    sampling_period : float
        How often to evaluate the latest qUnit bursts.
    threshold : float
        Activate only when the normalized sum is strictly greater than this
        value. Defaults to ``0.5``.
    default_input : float
        Value used for a qUnit that has not published yet. Defaults to ``0.0``.

    Attributes
    ----------
    name : str
        The actuator name.
    id : str
        Unique identifier for this actuator unit.
    threshold : float
        Activation threshold (normalized to [0, 1]).
    sampling_period : float
        How often to evaluate the latest qUnit bursts.
    default_input : float
        Fallback value when a qUnit has not published yet.

    """

    def __init__(
        self,
        name: str,
        in_qunits: list[str] | tuple[str, ...],
        sampling_period: float | int,
        threshold: float = 0.5,
        default_input: float = 0.0,
        redis_config: RedisConfig | None = None,
        logging_config: LoggingConfig | None = None,
    ) -> None:
        super().__init__(name, sampling_period, redis_config, logging_config)
        if not in_qunits or any(not isinstance(unit_id, str) for unit_id in in_qunits):
            raise ValueError("in_qunits must contain at least one qUnit id")
        self._in_qunits = tuple(in_qunits)
        self.threshold = self._normalized_value(threshold, "threshold")
        self.default_input = self._normalized_value(default_input, "default_input")

    def __iter__(self) -> Generator[tuple[str, object], None, None]:
        """Yield the actuator configuration as key-value pairs."""
        yield "name", self.name
        yield "id", self.id
        yield "in_qunits", self.in_qunits
        yield "threshold", self.threshold
        yield "sampling_period", self.sampling_period

    @property
    def in_qunits(self) -> dict[int, str]:
        """Input qUnit identifiers indexed for network visualization."""
        return dict(enumerate(self._in_qunits))

    @property
    def input_vector(self) -> list[float]:
        """Latest burst values, using the configured fallback when absent."""
        client = get_redis(self.redis_config)
        values = []
        for unit_id in self._in_qunits:
            value = client.get(build_redis_key(unit_id, RedisAttribute.OUTPUT))
            values.append(self.default_input if value is None else self._normalize_input(value))
        return values

    @property
    def normalized_sum(self) -> float:
        """Mean of the latest input bursts."""
        values = self.input_vector
        return sum(values) / len(values)

    def activation_for(self, normalized_sum: float) -> float:
        """Return the thresholded activation for a normalized input sum."""
        return threshold_activation(normalized_sum, self.threshold)

    def get_activation(self) -> float | None:
        """Return the latest activation published by this actuator."""
        value = get_redis(self.redis_config).get(build_redis_key(self.id, RedisAttribute.OUTPUT))
        return None if value is None else float(value)

    def _clean_redis(self) -> None:
        client = get_redis(self.redis_config)
        client.delete(
            build_redis_key(self.id, RedisAttribute.INPUT),
            build_redis_key(self.id, RedisAttribute.OUTPUT),
            build_redis_key(self.id, RedisAttribute.IN_QUNITS),
        )

    def _unit_task(self) -> None:
        normalized_sum = self.normalized_sum
        activation = self.activation_for(normalized_sum)
        client = get_redis(self.redis_config)
        try:
            written = client.mset(
                {
                    build_redis_key(self.id, RedisAttribute.INPUT): normalized_sum,
                    build_redis_key(self.id, RedisAttribute.OUTPUT): activation,
                    build_redis_key(self.id, RedisAttribute.IN_QUNITS): json.dumps(self.in_qunits),
                }
            )
        except redis.RedisError as exc:
            raise RedisWriteError(f"Unable to write ActuatorUnit {self.id} state to Redis") from exc
        if not written:
            raise RedisWriteError(f"Redis did not write ActuatorUnit {self.id} state")

    @staticmethod
    def _normalized_value(value: float, name: str) -> float:
        if not isinstance(value, (float, int)):
            raise TypeError(f"{name} must be a scalar number")
        if not 0.0 <= value <= 1.0:
            raise ValueError(f"{name} must be between 0 and 1")
        return float(value)

    def _normalize_input(self, value: object) -> float:
        """Return a normalized Redis burst, falling back when invalid."""
        try:
            normalized = float(value)  # type: ignore[arg-type]
        except (TypeError, ValueError):
            normalized = self.default_input
        if not 0.0 <= normalized <= 1.0:
            normalized = self.default_input
        return normalized


def threshold_activation(normalized_sum: float, threshold: float = 0.5) -> float:
    """Return ``1.0`` only when a normalized input is above the threshold."""
    value = ActuatorUnit._normalized_value(normalized_sum, "normalized_sum")
    limit = ActuatorUnit._normalized_value(threshold, "threshold")
    return float(value > limit)
