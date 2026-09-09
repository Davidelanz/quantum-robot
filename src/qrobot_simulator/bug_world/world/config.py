"""Configuration of the bug-world arena, population, sensors, and contacts."""

from dataclasses import dataclass
from math import pi

from ..robots.base_robot import MotionMode


@dataclass(frozen=True)
class WorldConfig:
    """Configure the arena, population, sensors, and interactions.

    :param board_columns: Horizontal checkerboard cells.
    :param board_rows: Vertical checkerboard cells.
    :param board_cell_size: Side length of one cell.
    :param prey_spawns: Name, pose, and motion mode of each prey.
    :param predator_spawn: Name and initial predator pose.
    :param proximity_distance: Maximum frontal proximity range.
    :param proximity_half_angle_degrees: Half-width of the proximity field.
    :param eye_angle: Offset of each eye ray from the bug heading.
    :param eye_distance_scale: Distance-response numerator of each eye.
    :param eye_angular_exponent: Concentration of the angular eye response.
    :param min_eye_distance: Lower distance bound in the eye response.
    :param bug_bite_reach: Bug reach beyond the two body radii.
    :param predator_bite_reach: Predator reach beyond the two body radii.
    :param bite_cue_duration: Seconds for which a bite highlight remains visible.
    """

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
