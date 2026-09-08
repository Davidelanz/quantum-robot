"""Immutable configuration for bug-world bodies and controllers."""

from dataclasses import dataclass
from math import pi
from typing import Literal, TypeAlias

QBrainTopology: TypeAlias = Literal["cognitive", "direct"]


@dataclass(frozen=True)
class RobotConfig:
    """Configure shared mobile-body geometry and command limits.

    :param radius: Body radius in world units.
    :param max_speed: Distance travelled per second at full command.
    :param max_turn: Radians turned per second at full command.
    :param turn_saturation_angle: Heading error producing a full turn command.
    :param min_normalized_command: Minimum accepted motion command.
    :param max_normalized_command: Maximum accepted motion command.
    """

    radius: float = 0.3
    max_speed: float = 1.0
    max_turn: float = 2.0
    turn_saturation_angle: float = pi / 3
    min_normalized_command: float = -1.0
    max_normalized_command: float = 1.0


@dataclass(frozen=True)
class BaseBugConfig:
    """Configure the body and shared sensor/action interface of a bug.

    :param name: Display and recording name.
    :param start_x: Initial horizontal coordinate.
    :param start_y: Initial vertical coordinate.
    :param start_heading: Initial orientation in radians.
    :param color: Matplotlib-compatible body color.
    :param radius: Body radius in world units.
    :param max_speed: Distance travelled per second at full command.
    :param max_turn: Radians turned per second at full command.
    :param sensor_keys: Ordered normalized sensor names.
    :param actuator_keys: Ordered normalized actuator names.
    :param bite_activation_threshold: Activation above which biting is active.
    :param forward_gain: Scale applied to forward activation.
    :param backward_gain: Scale applied to backward activation.
    :param rotation_gain: Scale applied to opposing rotation activations.
    """

    name: str = "bug"
    start_x: float = 5.5
    start_y: float = 4.0
    start_heading: float = 0.0
    color: str = "#704214"
    radius: float = RobotConfig.radius
    max_speed: float = RobotConfig.max_speed
    max_turn: float = 0.7
    sensor_keys: tuple[str, ...] = ("proximity", "lr", "lg", "lb", "rr", "rg", "rb")
    actuator_keys: tuple[str, ...] = (
        "bite",
        "forward",
        "backward",
        "rotate_left",
        "rotate_right",
    )
    bite_activation_threshold: float = 0.5
    forward_gain: float = 1.0
    backward_gain: float = 1.0
    rotation_gain: float = 1.0


@dataclass(frozen=True)
class ClassicalBugConfig(BaseBugConfig):
    """Configure the deterministic sensor-to-wheel controller.

    :param color_detection_threshold: Minimum red or blue evidence used as a target.
    :param proximity_threshold: Minimum proximity value permitting a bite.
    :param search_activation: Forward activation used without detected color.
    """

    color_detection_threshold: float = 0.25
    proximity_threshold: float = 0.5
    search_activation: float = 0.3


@dataclass(frozen=True)
class QuantumBugConfig(BaseBugConfig):
    """Configure qBrain timing, queries, connectivity, and thresholds.

    :param topology: Cognitive or direct perceptual-to-actuator connectivity.
    :param sensor_period: Wall-clock sensor and perceptual period at speed one.
    :param cognitive_period: Wall-clock cognitive and actuator period at speed one.
    :param perceptual_tau: Samples in each perceptual temporal window.
    :param cognitive_tau: Samples in each cognitive temporal window.
    :param proximity_query: Query used by the presence qUnit.
    :param red_query: RGB query used by red perceptual qUnits.
    :param blue_query: RGB query used by blue perceptual qUnits.
    :param bite_threshold: Normalized bite-actuator threshold.
    :param forward_threshold: Normalized forward-actuator threshold.
    :param backward_threshold: Normalized backward-actuator threshold.
    :param rotation_threshold: Threshold shared by both rotation actuators.
    """

    topology: QBrainTopology = "cognitive"
    sensor_period: float = 0.01
    cognitive_period: float = 0.1
    perceptual_tau: int = 10
    cognitive_tau: int = 5
    proximity_query: tuple[float, ...] = (1.0,)
    red_query: tuple[float, ...] = (1.0, 0.0, 0.0)
    blue_query: tuple[float, ...] = (0.0, 0.0, 1.0)
    bite_threshold: float = 0.75
    forward_threshold: float = 0.25
    backward_threshold: float = 0.75
    rotation_threshold: float = 0.75


@dataclass(frozen=True)
class PreyConfig:
    """Configure blue prey appearance and autonomous motion.

    :param color: Matplotlib-compatible body color.
    :param flee_distance: Hunter distance that overrides wandering.
    :param flee_speed: Normalized escape speed.
    :param wander_speed: Normalized undisturbed speed.
    :param deterministic_turn: Constant turn used by deterministic prey.
    :param random_turn_range: Bounds for random turn commands.
    :param random_choice_interval: Bounds between random command changes.
    :param initial_wander_turn: Turn used before the first random choice.
    """

    color: str = "#2878d0"
    flee_distance: float = 2.2
    flee_speed: float = RobotConfig.max_speed
    wander_speed: float = 0.55
    deterministic_turn: float = 0.22
    random_turn_range: tuple[float, float] = (-0.65, 0.65)
    random_choice_interval: tuple[float, float] = (0.7, 1.8)
    initial_wander_turn: float = 0.2


@dataclass(frozen=True)
class PredatorConfig:
    """Configure ideal-predator appearance, pursuit, and steering noise.

    :param color: Matplotlib-compatible body color.
    :param max_speed: Distance travelled per second at full command.
    :param pursuit_speed: Normalized speed used while chasing the bug.
    :param bite_period: Minimum seconds between scored contacts.
    :param random_noise_range: Bounds for optional steering noise.
    :param random_choice_interval: Bounds between random noise changes.
    """

    color: str = "#d43c32"
    max_speed: float = RobotConfig.max_speed
    pursuit_speed: float = 0.62
    bite_period: float = 3.0
    random_noise_range: tuple[float, float] = (-0.3, 0.3)
    random_choice_interval: tuple[float, float] = (0.8, 1.6)


ROBOT_CONFIG = RobotConfig()
BASE_BUG_CONFIG = BaseBugConfig()
CLASSICAL_BUG_CONFIG = ClassicalBugConfig()
QUANTUM_BUG_CONFIG = QuantumBugConfig()
PREY_CONFIG = PreyConfig()
PREDATOR_CONFIG = PredatorConfig()
