"""Configuration of the grasping arena, sensors, and physical interactions."""

from dataclasses import dataclass

from ..robots.config import GRIPPER_ROBOT_CONFIG

# World configuration


@dataclass(frozen=True)
class GraspingWorldConfig:
    """Configure arena geometry, sensing, grasping, and digestion."""

    # Sensor mapping
    near_distance: float = 5.0
    far_distance: float = 20.0
    # Physical interaction
    minimum_distance: float = 5.0
    grippable_distance: float = 15.0
    digestion_time: float = 2.5
    ball_distance_scale: float = 0.16
    sensor_offset_x: float = GRIPPER_ROBOT_CONFIG.half_width
    # Arena geometry
    arena_width: float = 12.0
    arena_height: float = 6.0
    arena_cell_size: float = 1.0


WORLD_CONFIG = GraspingWorldConfig()
