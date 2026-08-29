"""Configuration values for bug-world robot bodies and control policies."""

from dataclasses import dataclass
from math import pi


@dataclass(frozen=True)
class RobotConfig:
    """Default body dimensions and normalized motion-command limits."""

    radius: float = 0.3
    max_speed: float = 1.0
    max_turn: float = 2.0
    turn_saturation_angle: float = pi / 3
    min_normalized_command: float = -1.0
    max_normalized_command: float = 1.0


@dataclass(frozen=True)
class PreyConfig:
    """Appearance and autonomous movement settings for blue prey."""

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
    """Appearance, pursuit, bite cooldown, and steering noise of the predator."""

    color: str = "#d43c32"
    max_speed = RobotConfig.max_speed
    pursuit_speed: float = 0.62
    bite_period: float = 3.0
    random_noise_range: tuple[float, float] = (-0.3, 0.3)
    random_choice_interval: tuple[float, float] = (0.8, 1.6)


@dataclass(frozen=True)
class QBrainConfig:
    """Topology, timing, queries, thresholds, and body dynamics of the qBrain."""

    sensor_keys: tuple[str, ...] = ("proximity", "lr", "lg", "lb", "rr", "rg", "rb")
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
    forward_gain: float = 1.0
    backward_gain: float = 1.0
    rotation_gain: float = 1.0
    speed_time_constant: float = 0.45
    turn_time_constant: float = 0.2
    command_deadband: float = 0.05


@dataclass(frozen=True)
class BugConfig:
    """Initial pose, appearance, and physical limits of the qBrain bug."""

    name: str = "qBrain bug"
    start_x: float = 5.5
    start_y: float = 4.0
    start_heading: float = 0.0
    color: str = "#704214"
    max_speed = RobotConfig.max_speed
    max_turn: float = 0.7


ROBOT_CONFIG = RobotConfig()
PREY_CONFIG = PreyConfig()
PREDATOR_CONFIG = PredatorConfig()
QBRAIN_CONFIG = QBrainConfig()
BUG_CONFIG = BugConfig()
