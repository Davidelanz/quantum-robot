"""Configuration of the gripper robot, qBrain, and ball prey."""

from dataclasses import dataclass


@dataclass(frozen=True)
class GripperRobotConfig:
    """Configure the gripper robot's body and qBrain."""

    # Physical body
    x: float = 2.0
    y: float = 3.0
    color: str = "#704214"
    half_width: float = 0.55
    half_height: float = 0.65
    # qBrain timing and wiring
    sensor_keys: tuple[str, ...] = ("proximity", "touch")
    sampling_period: float = 0.1
    proximity_tau: int = 10
    empty_gripper_tau: int = 50
    gripper_threshold: float = 0.5
    max_simulation_speed: float = 10.0
    proximity_query: tuple[float, ...] = (1.0,)
    empty_gripper_query: tuple[float, ...] = (1.0,)
    touch_default_input: float = 1.0
    qunit_dimensions: int = 1


@dataclass(frozen=True)
class BallPreyConfig:
    """Configure the ball prey's appearance, spawning, and random motion."""

    # Appearance and physical limits
    radius: float = 0.32
    color: str = "#2878d0"
    max_distance: float = 45.0
    # Spawning and random movement
    initial_distance_range: tuple[float, float] = (24.0, 40.0)
    respawn_distance_range: tuple[float, float] = (30.0, 45.0)
    initial_velocity_range: tuple[float, float] = (-1.0, 1.0)
    velocity_kick_range: tuple[float, float] = (-4.0, 4.0)
    max_speed: float = 7.0
    motion_change_interval: tuple[float, float] = (0.35, 1.1)


GRIPPER_ROBOT_CONFIG = GripperRobotConfig()
BALL_PREY_CONFIG = BallPreyConfig()
