"""Physical gripper body and its Redis-connected qBrain."""

from dataclasses import dataclass

from qrobot.bursts import ZeroBurst
from qrobot.models import AngularModel
from qrobot_qunits import ActuatorUnit, QUnit, RedisConfig, SensorialUnit
from qrobot_qunits.redis import get_redis

from .config import GRIPPER_ROBOT_CONFIG

Sensors = dict[str, SensorialUnit]
QUnits = dict[str, QUnit]
GraspingQBrain = tuple[Sensors, QUnits, ActuatorUnit]


@dataclass(frozen=True)
class GraspingSignals:
    """Store observable qBrain outputs displayed by the live view.

    :param proximity_burst: Latest distance-perception burst.
    :param empty_gripper_burst: Latest touch-perception burst.
    :param gripper_activation: Latest actuator output.
    """

    proximity_burst: float | None
    empty_gripper_burst: float | None
    gripper_activation: float | None


class GraspingRobot:
    """Represent the stationary gripper body and its optional qBrain."""

    def __init__(
        self,
        redis_config: RedisConfig | None = None,
        speed: float = 1.0,
        *,
        connect_brain: bool = True,
    ) -> None:
        """Initialize the physical body and optionally construct its qBrain.

        :param redis_config: Redis connection shared by all qBrain workers.
        :param speed: Simulation-time to wall-clock-time ratio.
        :param connect_brain: Construct Redis-backed units when true.
        """
        self.x = GRIPPER_ROBOT_CONFIG.x
        self.y = GRIPPER_ROBOT_CONFIG.y
        self.color = GRIPPER_ROBOT_CONFIG.color
        self.gripper_closed = False
        self.redis_config = redis_config or RedisConfig()
        self.sensors: Sensors
        self.qunits: QUnits
        self.actuator: ActuatorUnit | None
        if connect_brain:
            self.sensors, self.qunits, self.actuator = build_grasping_qbrain(
                self.redis_config, speed
            )
        else:
            self.sensors, self.qunits, self.actuator = {}, {}, None

    # Public physical and qBrain interface

    def apply_activation(self, activation: float) -> None:
        """Map a normalized actuator value to the binary gripper state.

        :param activation: Latest actuator output.
        """
        self.gripper_closed = activation > GRIPPER_ROBOT_CONFIG.gripper_threshold

    def perceive(self, readings: dict[str, float]) -> None:
        """Copy normalized proximity and touch readings to the sensor units.

        :param readings: Values keyed by configured sensor name.
        :raises KeyError: If a reading names a sensor not present in the qBrain.
        """
        for name, value in readings.items():
            self.sensors[name].scalar_reading = value

    def signals(self) -> GraspingSignals:
        """Read the latest perceptual and actuator outputs.

        :returns: Current qBrain outputs, including unpublished ``None`` values.
        """
        if self.actuator is None:
            return GraspingSignals(None, None, None)
        return GraspingSignals(
            self.qunits["proximity"].get_burst_output(),
            self.qunits["empty_gripper"].get_burst_output(),
            self.actuator.get_activation(),
        )

    def actuator_value(self) -> float:
        """Return the latest actuator output.

        :returns: Current activation, or zero before publication.
        """
        return 0.0 if self.actuator is None else self.actuator.get_activation() or 0.0

    @property
    def brain_units(self) -> tuple[SensorialUnit | QUnit | ActuatorUnit, ...]:
        """Return every qBrain worker in startup order.

        :returns: Sensors, qUnits, and the actuator when connected.
        """
        actuator = () if self.actuator is None else (self.actuator,)
        return (*self.sensors.values(), *self.qunits.values(), *actuator)

    def start_brain(self) -> None:
        """Start all independently scheduled qBrain workers."""
        for unit in self.brain_units:
            unit.start()

    def stop_brain(self) -> None:
        """Stop workers and remove their Redis keys."""
        units = self.brain_units
        if not units:
            return
        for unit in reversed(units):
            unit.stop()
        client = get_redis(self.redis_config)
        keys = [key for unit in units for key in client.scan_iter(match=f"{unit.id} *")]
        if keys:
            client.delete(*keys)


# Public qBrain construction


def build_grasping_qbrain(redis_config: RedisConfig, speed: float = 1.0) -> GraspingQBrain:
    """Construct the two-sensor, two-qUnit, one-actuator qBrain.

    :param redis_config: Redis connection shared by every processing unit.
    :param speed: Positive simulation-time to wall-clock-time ratio.
    :returns: Sensor dictionary, qUnit dictionary, and gripper actuator.
    :raises ValueError: If ``speed`` is outside the configured range.
    """
    if not 0 < speed <= GRIPPER_ROBOT_CONFIG.max_simulation_speed:
        raise ValueError(
            "speed must be greater than zero and at most "
            f"{GRIPPER_ROBOT_CONFIG.max_simulation_speed:g}"
        )
    period = GRIPPER_ROBOT_CONFIG.sampling_period / speed
    sensors = _build_sensors(redis_config, period)
    qunits = _build_qunits(sensors, redis_config, period)
    actuator = ActuatorUnit(
        "grasp_gripper",
        [qunits["proximity"].id, qunits["empty_gripper"].id],
        period,
        threshold=GRIPPER_ROBOT_CONFIG.gripper_threshold,
        redis_config=redis_config,
    )
    return sensors, qunits, actuator


# Internal qBrain layers


def _build_sensors(redis_config: RedisConfig, period: float) -> Sensors:
    """Build the distance and internal touch sensor interfaces."""
    return {
        "proximity": SensorialUnit("grasp_distance", period, redis_config=redis_config),
        "touch": SensorialUnit(
            "grasp_touch",
            period,
            default_input=GRIPPER_ROBOT_CONFIG.touch_default_input,
            redis_config=redis_config,
        ),
    }


def _build_qunits(sensors: Sensors, redis_config: RedisConfig, period: float) -> QUnits:
    """Build the fast proximity and slow empty-gripper feature detectors."""
    return {
        "proximity": QUnit(
            "grasp_proximity",
            AngularModel(
                n=GRIPPER_ROBOT_CONFIG.qunit_dimensions,
                tau=GRIPPER_ROBOT_CONFIG.proximity_tau,
            ),
            ZeroBurst(),
            period,
            query=list(GRIPPER_ROBOT_CONFIG.proximity_query),
            in_qunits={0: sensors["proximity"].id},
            redis_config=redis_config,
        ),
        "empty_gripper": QUnit(
            "grasp_empty",
            AngularModel(
                n=GRIPPER_ROBOT_CONFIG.qunit_dimensions,
                tau=GRIPPER_ROBOT_CONFIG.empty_gripper_tau,
            ),
            ZeroBurst(),
            period,
            query=list(GRIPPER_ROBOT_CONFIG.empty_gripper_query),
            in_qunits={0: sensors["touch"].id},
            redis_config=redis_config,
        ),
    }
