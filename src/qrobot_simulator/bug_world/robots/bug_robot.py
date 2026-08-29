"""Bug body, qBrain construction, and Redis lifecycle management."""

from qrobot.bursts import OneBurst, ZeroBurst
from qrobot.models import AngularModel
from qrobot_qunits import ActuatorUnit, QUnit, RedisConfig, SensorialUnit, redis_utils

from .base import Robot
from .config import BUG_CONFIG, QBRAIN_CONFIG

Sensors = dict[str, SensorialUnit]
QUnits = dict[str, QUnit]
Actuators = dict[str, ActuatorUnit]
QBrain = tuple[Sensors, QUnits, Actuators]


class BugRobot(Robot):
    """Represent the actuator-driven bug body and its qBrain units."""

    def __init__(
        self,
        redis_config: RedisConfig | None = None,
        *,
        connect_brain: bool = True,
    ) -> None:
        """Initialize the bug body and optionally construct its qBrain.

        :param redis_config: Redis connection shared by every qBrain unit. A default
            local configuration is created when omitted.
        :param connect_brain: Construct the Redis-backed processing units when true.
        """
        super().__init__(
            BUG_CONFIG.name,
            BUG_CONFIG.start_x,
            BUG_CONFIG.start_y,
            BUG_CONFIG.start_heading,
            BUG_CONFIG.color,
            max_speed=BUG_CONFIG.max_speed,
            max_turn=BUG_CONFIG.max_turn,
        )
        self.behavior = "SEARCH"
        self.biting = False
        self._speed_command = 0.0
        self._turn_command = 0.0
        self.redis_config = redis_config or RedisConfig()
        self.sensors: Sensors
        self.qunits: QUnits
        self.actuators: Actuators
        if connect_brain:
            self.sensors, self.qunits, self.actuators = build_bug_qbrain(self.redis_config)
        else:
            self.sensors, self.qunits, self.actuators = {}, {}, {}

    # Public simulation interface

    def step(
        self,
        activations: dict[str, float],
        dt: float,
        bounds: tuple[float, float],
    ) -> None:
        """Interpret actuator values and advance the body.

        :param activations: Current values keyed by configured actuator name.
        :param dt: Simulation interval in seconds.
        :param bounds: Arena ``(width, height)`` in world units.
        """
        speed, turn = self._target_commands(activations)
        self.behavior = self._behavior_label(speed, turn, activations.get("forward", 0.0))
        self.move(speed, turn, dt, bounds)

    def perceive(self, readings: dict[str, float]) -> None:
        """Copy world readings into the corresponding sensor interfaces.

        :param readings: Normalized readings keyed by configured sensor name.
        :raises KeyError: If a reading names a sensor not present in the qBrain.
        """
        for name, value in readings.items():
            self.sensors[name].scalar_reading = value

    def qunint_values(self) -> dict[str, float]:
        """Read the latest burts of every qunit.

        :returns: Bursts keyed by qunit name; unavailable values become zero.
        """
        return {name: qunit.get_burst_output() or 0.0 for name, qunit in self.qunits.items()}

    def actuator_values(self) -> dict[str, float]:
        """Read the current activation of every actuator.

        :returns: Activations keyed by actuator name; unavailable values become zero.
        """
        return {name: actuator.get_activation() or 0.0 for name, actuator in self.actuators.items()}

    @property
    def brain_units(self) -> tuple[SensorialUnit | QUnit | ActuatorUnit, ...]:
        """Return all independently scheduled qBrain units in startup order.

        :returns: Sensors, qUnits, and actuators in lifecycle order.
        """
        return (*self.sensors.values(), *self.qunits.values(), *self.actuators.values())

    def start_brain(self) -> None:
        """Start all sensor, perceptual, cognitive, and actuator workers."""
        for unit in self.brain_units:
            unit.start()

    def stop_brain(self) -> None:
        """Stop all workers and delete their Redis keys."""
        units = self.brain_units
        if not units:
            return
        for unit in reversed(units):
            unit.stop()
        client = redis_utils.get_redis(self.redis_config)
        keys = [key for unit in units for key in client.scan_iter(match=f"{unit.id} *")]
        if keys:
            client.delete(*keys)

    # Internal actuator interpretation

    def _target_commands(self, activations: dict[str, float]) -> tuple[float, float]:
        """Combine opposing actuators into signed speed and turn targets."""
        forward = activations.get("forward", 0.0)
        backward = activations.get("backward", 0.0)
        left = activations.get("rotate_left", 0.0)
        right = activations.get("rotate_right", 0.0)
        self.biting = activations.get("bite", 0.0) > QBRAIN_CONFIG.bite_threshold
        speed = QBRAIN_CONFIG.forward_gain * forward - QBRAIN_CONFIG.backward_gain * backward
        turn = QBRAIN_CONFIG.rotation_gain * (left - right)
        return speed, turn

    def _behavior_label(self, speed: float, turn: float, forward: float) -> str:
        """Translate the effective command into a concise display label."""
        if self.biting:
            return "BITE"
        if speed > 0 and turn:
            return "FWD LEFT" if turn > 0 else "FWD RIGHT"
        if speed < 0 or (turn and not forward):
            return "BACK LEFT" if turn > 0 else "BACK RIGHT"
        if speed > 0:
            return "FORWARD"
        if turn:
            return "TURN LEFT" if turn > 0 else "TURN RIGHT"
        return ""


# Public qBrain construction


def build_bug_qbrain(redis_config: RedisConfig) -> QBrain:
    """Construct and connect the bug's complete qBrain topology.

    :param redis_config: Redis connection shared by all processing units.
    :returns: Dictionaries containing sensors, qUnits, and actuators.
    """
    # Define the sensor
    sensors = {}
    for name in QBRAIN_CONFIG.sensor_keys:
        sensors[name] = SensorialUnit(
            "bug_" + name,
            QBRAIN_CONFIG.sensor_period,
            redis_config=redis_config,
        )

    # Define the perceptual units
    qunits = {}
    perceptual_definitions = {
        "presence": (
            {0: sensors["proximity"].id},
            QBRAIN_CONFIG.proximity_query,
        ),
        "left_red": (
            {0: sensors["lr"].id, 1: sensors["lg"].id, 2: sensors["lb"].id},
            QBRAIN_CONFIG.red_query,
        ),
        "left_blue": (
            {0: sensors["lr"].id, 1: sensors["lg"].id, 2: sensors["lb"].id},
            QBRAIN_CONFIG.blue_query,
        ),
        "right_red": (
            {0: sensors["rr"].id, 1: sensors["rg"].id, 2: sensors["rb"].id},
            QBRAIN_CONFIG.red_query,
        ),
        "right_blue": (
            {0: sensors["rr"].id, 1: sensors["rg"].id, 2: sensors["rb"].id},
            QBRAIN_CONFIG.blue_query,
        ),
    }
    for key, (in_qunits, query) in perceptual_definitions.items():
        qunits[key] = QUnit(
            name="bug_" + key,
            model=AngularModel(n=len(in_qunits), tau=QBRAIN_CONFIG.perceptual_tau),
            burst=ZeroBurst(),
            sampling_period=QBRAIN_CONFIG.sensor_period,
            query=list(query),
            in_qunits=in_qunits,
            redis_config=redis_config,
        )

    # Define the cognitive units
    cognitive_definitions = {
        "prey": ({0: qunits["presence"].id, 1: qunits["left_blue"].id, 2: qunits["right_blue"].id}),
        "threat": ({0: qunits["presence"].id, 1: qunits["left_red"].id, 2: qunits["right_red"].id}),
    }
    for key, (in_qunits) in cognitive_definitions.items():
        qunits[key] = QUnit(
            name="bug_" + key,
            model=AngularModel(n=len(in_qunits), tau=QBRAIN_CONFIG.cognitive_tau),
            burst=OneBurst(),
            sampling_period=QBRAIN_CONFIG.cognitive_period,
            in_qunits=in_qunits,
            redis_config=redis_config,
        )

    # Define the actuators
    actuators = {}
    actuator_definitions = {
        "bite": (
            [qunits["presence"].id, qunits["prey"].id],
            QBRAIN_CONFIG.bite_threshold,
        ),
        "forward": (
            [qunits["prey"].id],
            QBRAIN_CONFIG.forward_threshold,
        ),
        "backward": (
            [qunits["threat"].id],
            QBRAIN_CONFIG.backward_threshold,
        ),
        "rotate_left": (
            [qunits["left_blue"].id, qunits["right_red"].id],
            QBRAIN_CONFIG.rotation_threshold,
        ),
        "rotate_right": (
            [qunits["left_red"].id, qunits["right_blue"].id],
            QBRAIN_CONFIG.rotation_threshold,
        ),
    }
    for name, (input_ids, threshold) in actuator_definitions.items():
        actuators[name] = ActuatorUnit(
            name="bug_" + name,
            in_qunits=input_ids,
            sampling_period=QBRAIN_CONFIG.cognitive_period,
            threshold=threshold,
            redis_config=redis_config,
        )

    return sensors, qunits, actuators
