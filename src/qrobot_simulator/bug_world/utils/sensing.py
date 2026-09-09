"""Sensor-response functions used by the bug world and renderer."""

from math import cos

from ..world.config import WORLD_CONFIG, WorldConfig
from .geometry import wrap_angle


def eye_response_strength(
    distance: float,
    bearing: float,
    ray_angle: float,
    config: WorldConfig = WORLD_CONFIG,
) -> float:
    """Calculate one eye ray's normalized angular and distance response."""
    delta = abs(wrap_angle(bearing - ray_angle))
    angular_response = max(0.0, cos(delta)) ** config.eye_angular_exponent
    distance_response = config.eye_distance_scale / max(distance, config.min_eye_distance)
    return min(1.0, angular_response * distance_response)
