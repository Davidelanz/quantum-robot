"""Bounded-motion integration for circular bug-world bodies."""

from math import cos, sin

from .geometry import wrap_angle, wrap_coordinate


def integrate_motion(
    position: tuple[float, float],
    heading: float,
    radius: float,
    limits: tuple[float, float],
    commands: tuple[float, float],
    dt: float,
    bounds: tuple[float, float],
) -> tuple[float, float, float, bool]:
    """Advance one pose and report whether it crossed the toroidal boundary."""
    max_speed, max_turn = limits
    speed, turn = commands
    next_heading = wrap_angle(heading + max_turn * turn * dt)
    next_x = position[0] + max_speed * speed * cos(next_heading) * dt
    next_y = position[1] + max_speed * speed * sin(next_heading) * dt
    width, height = bounds
    crossed = not (radius <= next_x <= width - radius and radius <= next_y <= height - radius)
    return (
        wrap_coordinate(next_x, radius, width),
        wrap_coordinate(next_y, radius, height),
        next_heading,
        crossed,
    )
