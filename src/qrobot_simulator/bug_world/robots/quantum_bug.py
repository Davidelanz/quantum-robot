"""Quantum bug and its Redis-connected qBrain."""

from collections.abc import Mapping
from time import monotonic, sleep

from qrobot.bursts import OneBurst, ZeroBurst
from qrobot.models import AngularModel
from qrobot_qunits import ActuatorUnit, QUnit, RedisConfig, SensorialUnit
from qrobot_qunits.redis import get_redis, read_outputs

from .base_bug import Activations, BaseBug, BaseBugBrain, Diagnostics, Readings
from .config import QUANTUM_BUG_CONFIG, QuantumBugConfig

Sensors = dict[str, SensorialUnit]
QUnits = dict[str, QUnit]
Actuators = dict[str, ActuatorUnit]

WORKER_STARTUP_ALLOWANCE = 1.0
"""Conservative process-spawn allowance per qBrain unit, in seconds."""


class QuantumBugBrain(BaseBugBrain):
    """Build and operate the complete perceptual and cognitive qBrain.

    :param redis_config: Redis database shared by all processing units.
    :param speed: Ratio between simulated time and wall-clock time.
    :param config: qBrain topology, timing, models, queries, and thresholds.
    """

    def __init__(
        self,
        redis_config: RedisConfig | None = None,
        speed: float = 1.0,
        config: QuantumBugConfig = QUANTUM_BUG_CONFIG,
    ) -> None:
        """Construct sensors, qUnits, and actuators in their signal order."""
        if speed <= 0:
            raise ValueError("speed must be positive")
        if config.topology not in ("cognitive", "direct"):
            raise ValueError(f"unknown qBrain topology: {config.topology}")
        self.redis_config = redis_config or RedisConfig()
        self.speed = speed
        sensor_period = config.sensor_period / speed
        cognitive_period = config.cognitive_period / speed

        # The seven sensorial units expose proximity and both RGB eye vectors.
        self.sensors: Sensors = {
            name: SensorialUnit(f"bug_{name}", sensor_period, redis_config=self.redis_config)
            for name in config.sensor_keys
        }

        # Perceptual qUnits query short histories for presence and target colors.
        definitions = {
            "presence": ({0: self.sensors["proximity"].id}, config.proximity_query),
            "left_red": (self._eye_inputs("l"), config.red_query),
            "left_blue": (self._eye_inputs("l"), config.blue_query),
            "right_red": (self._eye_inputs("r"), config.red_query),
            "right_blue": (self._eye_inputs("r"), config.blue_query),
        }
        self.qunits: QUnits = {
            name: QUnit(
                name=f"bug_{name}",
                model=AngularModel(n=len(inputs), tau=config.perceptual_tau),
                burst=ZeroBurst(),
                sampling_period=sensor_period,
                query=list(query),
                in_qunits=inputs,
                redis_config=self.redis_config,
            )
            for name, (inputs, query) in definitions.items()
        }

        # The complete topology integrates perceptual decisions into explicit
        # prey and threat concepts. The direct topology omits only this layer.
        if config.topology == "cognitive":
            for name, inputs in {
                "prey": {
                    0: self.qunits["presence"].id,
                    1: self.qunits["left_blue"].id,
                    2: self.qunits["right_blue"].id,
                },
                "threat": {
                    0: self.qunits["presence"].id,
                    1: self.qunits["left_red"].id,
                    2: self.qunits["right_red"].id,
                },
            }.items():
                self.qunits[name] = QUnit(
                    name=f"bug_{name}",
                    model=AngularModel(n=len(inputs), tau=config.cognitive_tau),
                    burst=OneBurst(),
                    sampling_period=cognitive_period,
                    in_qunits=inputs,
                    redis_config=self.redis_config,
                )

        # Both topologies expose the same five actions to the common bug body.
        semantics = self._semantic_inputs(config)
        actuator_definitions = {
            "bite": (
                [self.qunits["presence"].id, *semantics["prey"]],
                config.bite_threshold,
            ),
            "forward": (semantics["prey"], config.forward_threshold),
            "backward": (semantics["threat"], config.backward_threshold),
            "rotate_left": (
                [self.qunits["left_blue"].id, self.qunits["right_red"].id],
                config.rotation_threshold,
            ),
            "rotate_right": (
                [self.qunits["left_red"].id, self.qunits["right_blue"].id],
                config.rotation_threshold,
            ),
        }
        self.actuators: Actuators = {
            name: ActuatorUnit(
                name=f"bug_{name}",
                in_qunits=inputs,
                sampling_period=cognitive_period,
                threshold=threshold,
                redis_config=self.redis_config,
            )
            for name, (inputs, threshold) in actuator_definitions.items()
        }
        longest_window = max(
            config.perceptual_tau * sensor_period,
            config.cognitive_tau * cognitive_period if config.topology == "cognitive" else 0.0,
        )
        self.readiness_timeout = max(
            5.0,
            len(self.units) * WORKER_STARTUP_ALLOWANCE + longest_window + cognitive_period,
        )

    @property
    def units(self) -> tuple[SensorialUnit | QUnit | ActuatorUnit, ...]:
        """Return every qBrain worker in startup order."""
        return (*self.sensors.values(), *self.qunits.values(), *self.actuators.values())

    def start(self, readings: Readings) -> None:
        """Publish initial readings before starting every qBrain worker."""
        self._perceive(readings)
        for unit in self.units:
            unit.start()

    @property
    def ready(self) -> bool:
        """Return whether every actuator has published its first value."""
        return all(value is not None for value in self._read_values(self.actuators, None).values())

    def command(self, readings: Readings, dt: float) -> Activations:
        """Publish readings and obtain actions after one real-time interval."""
        if dt <= 0:
            raise ValueError("dt must be positive")
        started = monotonic()
        self._perceive(readings)
        sleep(max(0.0, dt / self.speed - (monotonic() - started)))
        return {
            name: float(value or 0.0)
            for name, value in self._read_values(self.actuators, 0.0).items()
        }

    def stop(self) -> None:
        """Stop every worker and remove only this qBrain's Redis keys."""
        for unit in reversed(self.units):
            unit.stop()
        client = get_redis(self.redis_config)
        keys = [key for unit in self.units for key in client.scan_iter(match=f"{unit.id} *")]
        if keys:
            client.delete(*keys)

    def diagnostics(self) -> Diagnostics:
        """Return all qUnit bursts and actuator activations by semantic name."""
        qvalues = self._read_values(self.qunits, None)
        activations = self._read_values(self.actuators, None)
        return {
            **{f"{name}_burst": value for name, value in qvalues.items()},
            **{f"{name}_activation": value for name, value in activations.items()},
        }

    def _eye_inputs(self, eye: str) -> dict[int, str]:
        """Return the ordered RGB sensor identifiers for one eye."""
        return {index: self.sensors[f"{eye}{channel}"].id for index, channel in enumerate("rgb")}

    def _semantic_inputs(self, config: QuantumBugConfig) -> dict[str, list[str]]:
        """Select cognitive or direct perceptual inputs for semantic actions."""
        if config.topology == "cognitive":
            return {
                "prey": [self.qunits["prey"].id],
                "threat": [self.qunits["threat"].id],
            }
        return {
            "prey": [self.qunits["left_blue"].id, self.qunits["right_blue"].id],
            "threat": [self.qunits["left_red"].id, self.qunits["right_red"].id],
        }

    def _perceive(self, readings: Readings) -> None:
        """Copy normalized world readings to their sensorial units."""
        for name, value in readings.items():
            self.sensors[name].scalar_reading = value

    def _read_values(
        self,
        units: Mapping[str, QUnit | ActuatorUnit],
        missing: float | None,
    ) -> dict[str, float | None]:
        """Read a named group of qBrain outputs in one Redis request."""
        names = list(units)
        values = read_outputs(
            get_redis(self.redis_config),
            [units[name].id for name in names],
        )
        return {
            name: missing if value is None else float(value)
            for name, value in zip(names, values, strict=True)
        }


class QuantumBug(BaseBug):
    """Physical bug driven by an injectable quantum or alternative brain.

    :param redis_config: Redis database used by the default qBrain.
    :param speed: Ratio between simulated time and wall-clock time.
    :param config: Body and qBrain configuration.
    :param brain: Complete alternative brain, or ``None`` for the default.
    """

    def __init__(
        self,
        redis_config: RedisConfig | None = None,
        speed: float = 1.0,
        config: QuantumBugConfig = QUANTUM_BUG_CONFIG,
        brain: BaseBugBrain | None = None,
    ) -> None:
        """Construct the configured qBrain unless another brain is supplied."""
        selected_brain = (
            brain if brain is not None else QuantumBugBrain(redis_config, speed, config)
        )
        super().__init__(config, selected_brain)
