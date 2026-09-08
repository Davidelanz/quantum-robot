"""Quantum gripper and its Redis-connected qBrain."""

from time import monotonic, sleep

from qrobot.bursts import ZeroBurst
from qrobot.models import AngularModel
from qrobot_qunits import ActuatorUnit, QUnit, RedisConfig, SensorialUnit
from qrobot_qunits.redis import get_redis, read_outputs

from .base_gripper import BaseGripper, BaseGripperBrain, Diagnostics, Readings
from .config import QUANTUM_GRIPPER_CONFIG, QuantumGripperConfig

Sensors = dict[str, SensorialUnit]
QUnits = dict[str, QUnit]


class QuantumGripperBrain(BaseGripperBrain):
    """Bridge common readings and actions to independently scheduled qUnits."""

    def __init__(
        self,
        redis_config: RedisConfig | None = None,
        speed: float = 1.0,
        config: QuantumGripperConfig = QUANTUM_GRIPPER_CONFIG,
    ) -> None:
        """Construct the complete sensor--qUnit--actuator qBrain."""
        if speed <= 0:
            raise ValueError("speed must be positive")
        self.redis_config = redis_config or RedisConfig()
        self.speed = speed
        period = config.sampling_period / speed

        # Sensor interfaces publish the normalized values supplied by the world.
        self.sensors = {
            "proximity": SensorialUnit("grasp_distance", period, redis_config=self.redis_config),
            "touch": SensorialUnit(
                "grasp_touch",
                period,
                default_input=config.touch_default_input,
                redis_config=self.redis_config,
            ),
        }

        # The qUnits integrate proximity quickly and empty-gripper feedback slowly.
        self.qunits = {
            "proximity": QUnit(
                "grasp_proximity",
                AngularModel(n=config.qunit_dimensions, tau=config.proximity_tau),
                ZeroBurst(),
                period,
                query=list(config.proximity_query),
                in_qunits={0: self.sensors["proximity"].id},
                redis_config=self.redis_config,
            ),
            "empty_gripper": QUnit(
                "grasp_empty",
                AngularModel(n=config.qunit_dimensions, tau=config.empty_gripper_tau),
                ZeroBurst(),
                period,
                query=list(config.empty_gripper_query),
                in_qunits={0: self.sensors["touch"].id},
                redis_config=self.redis_config,
            ),
        }

        # The actuator combines the two perceptual outputs into the jaw command.
        self.actuator = ActuatorUnit(
            "grasp_gripper",
            [self.qunits["proximity"].id, self.qunits["empty_gripper"].id],
            period,
            threshold=config.gripper_threshold,
            redis_config=self.redis_config,
        )
        slowest_window = max(unit.model.tau for unit in self.qunits.values())
        self.readiness_timeout = max(5.0, slowest_window * self.actuator.sampling_period + 2.0)

    @property
    def units(self) -> tuple[SensorialUnit | QUnit | ActuatorUnit, ...]:
        """Return every qBrain worker in startup order."""
        return (*self.sensors.values(), *self.qunits.values(), self.actuator)

    def start(self, readings: Readings) -> None:
        """Publish the initial readings and start every qBrain worker."""
        self._perceive(readings)
        for unit in self.units:
            unit.start()

    @property
    def ready(self) -> bool:
        """Return whether both temporal qUnits have published an output."""
        values = self.diagnostics()
        return values["proximity_burst"] is not None and values["empty_gripper_burst"] is not None

    def command(self, readings: Readings, dt: float) -> float:
        """Publish readings and sample the actuator after one real-time step."""
        if dt <= 0:
            raise ValueError("dt must be positive")
        started = monotonic()
        self._perceive(readings)

        # Worker processes need their corresponding wall-time interval before
        # the actuator value represents this simulated step.
        sleep(max(0.0, dt / self.speed - (monotonic() - started)))
        return self.actuator.get_activation() or 0.0

    def stop(self) -> None:
        """Stop every worker and remove only this qBrain's Redis keys."""
        for unit in reversed(self.units):
            unit.stop()
        client = get_redis(self.redis_config)
        keys = [key for unit in self.units for key in client.scan_iter(match=f"{unit.id} *")]
        if keys:
            client.delete(*keys)

    def diagnostics(self) -> Diagnostics:
        """Read perceptual bursts and actuator output for the live view."""
        values = read_outputs(
            get_redis(self.redis_config),
            (self.qunits["proximity"].id, self.qunits["empty_gripper"].id, self.actuator.id),
        )
        proximity, empty_gripper, activation = (
            None if value is None else float(value) for value in values
        )
        return {
            "proximity_burst": proximity,
            "empty_gripper_burst": empty_gripper,
            "gripper_activation": activation,
        }

    def _perceive(self, readings: Readings) -> None:
        """Copy normalized world readings to the qBrain sensor interfaces."""
        for name, value in readings.items():
            self.sensors[name].scalar_reading = value


class QuantumGripper(BaseGripper):
    """Physical gripper driven by an injectable quantum or alternative brain."""

    def __init__(
        self,
        redis_config: RedisConfig | None = None,
        speed: float = 1.0,
        config: QuantumGripperConfig = QUANTUM_GRIPPER_CONFIG,
        brain: BaseGripperBrain | None = None,
    ) -> None:
        """Build the configured qBrain unless a complete brain is supplied."""
        selected_brain = (
            brain if brain is not None else QuantumGripperBrain(redis_config, speed, config)
        )
        super().__init__(config, selected_brain)
