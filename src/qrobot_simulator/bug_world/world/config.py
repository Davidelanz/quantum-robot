"""Configuration of the bug-world arena, population, sensors, and contacts."""

from dataclasses import dataclass
from math import pi

from ..robots.base import MotionMode


@dataclass(frozen=True)
class WorldConfig:
    """Arena, population, sensing, and interaction settings of the bug world."""

    board_columns: int = 18
    board_rows: int = 12
    board_cell_size: float = 1.0
    prey_spawns: tuple[tuple[str, float, float, float, MotionMode], ...] = (
        ("prey 1", 9.5, 6.2, pi, "deterministic"),
        ("prey 2", 8.8, 1.6, 2.6, "random"),
    )
    predator_spawn: tuple[str, float, float, float] = (
        "predator",
        1.5,
        6.5,
        -0.5,
    )
    proximity_distance: float = 1.25
    proximity_half_angle_degrees: float = 25.0
    eye_angle: float = pi / 6
    eye_distance_scale: float = 4.5
    eye_angular_exponent: int = 12
    min_eye_distance: float = 0.1
    bug_bite_reach: float = 0.45
    predator_bite_reach: float = 0.15
    bite_cue_duration: float = 0.45


WORLD_CONFIG = WorldConfig()
