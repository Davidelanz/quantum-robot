"""Reusable two-dimensional geometry helpers for the bug world."""

from math import atan2, pi
from typing import Protocol

Point = tuple[float, float]
Bounds = tuple[float, float]


class PositionedBody(Protocol):
    """Describe a circular body accepted by the contact helpers."""

    x: float
    y: float
    radius: float


# Angle and coordinate normalization


def wrap_angle(angle: float) -> float:
    """Wrap an angle to the half-open interval ``[-pi, pi)``.

    :param angle: Angle in radians.
    :returns: Equivalent wrapped angle in radians.
    """
    return (angle + pi) % (2 * pi) - pi


def wrap_coordinate(position: float, radius: float, extent: float) -> float:
    """Wrap a body-centre coordinate through opposite arena edges.

    :param position: Coordinate after applying motion.
    :param radius: Body radius reserved at either edge.
    :param extent: Total width or height of the arena.
    :returns: Equivalent coordinate inside the radius-safe interval.
    """
    usable_extent = extent - 2 * radius
    return (position - radius) % usable_extent + radius


# Circular-body contact geometry


def contact_distance(first: PositionedBody, second: PositionedBody, reach: float = 0.0) -> float:
    """Calculate the centre distance at which two circular bodies interact.

    :param first: First circular body.
    :param second: Second circular body.
    :param reach: Additional interaction margin outside both body radii.
    :returns: Centre-to-centre interaction distance.
    """
    return first.radius + second.radius + reach


def radius_safe_corners(bounds: Bounds, radius: float) -> tuple[Point, ...]:
    """Return the four radius-safe arena corners.

    :param bounds: Arena ``(width, height)``.
    :param radius: Radius to reserve from every edge.
    :returns: Four valid body-centre positions.
    """
    width, height = bounds
    return (
        (radius, radius),
        (radius, height - radius),
        (width - radius, radius),
        (width - radius, height - radius),
    )


def farthest_point(origin: Point, candidates: tuple[Point, ...], tie_breaker: int = 0) -> Point:
    """Select a farthest candidate from an origin.

    :param origin: Reference ``(x, y)`` point.
    :param candidates: Candidate points to compare.
    :param tie_breaker: Index used modulo the number of equally far points.
    :returns: Selected farthest point.
    :raises ValueError: If ``candidates`` is empty.
    """
    origin_x, origin_y = origin
    distances = tuple((x - origin_x) ** 2 + (y - origin_y) ** 2 for x, y in candidates)
    greatest = max(distances)
    farthest = tuple(
        point for point, distance in zip(candidates, distances, strict=True) if distance == greatest
    )
    return farthest[tie_breaker % len(farthest)]


def heading_to_point(origin: Point, target: Point) -> float:
    """Calculate the absolute heading from an origin to a target.

    :param origin: Starting ``(x, y)`` point.
    :param target: Destination ``(x, y)`` point.
    :returns: Heading in radians.
    """
    return atan2(target[1] - origin[1], target[0] - origin[0])
