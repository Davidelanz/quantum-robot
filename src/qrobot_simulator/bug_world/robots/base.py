"""Shared geometry and motion primitives for the bug-world robots."""

from dataclasses import dataclass
from math import atan2, cos, hypot, sin
from typing import Literal, TypeAlias

from ..utils.geometry import wrap_angle, wrap_coordinate
from .config import ROBOT_CONFIG

MotionMode: TypeAlias = Literal["deterministic", "random"]


@dataclass
class Robot:
    """Circular mobile body in a bounded two-dimensional arena.

    :param name: Stable label used by the renderer to identify the robot.
    :param x: Horizontal position in arena units.
    :param y: Vertical position in arena units.
    :param heading: Direction of travel in radians, measured counter-clockwise.
    :param color: Matplotlib-compatible display color.
    :param radius: Collision and display radius in arena units.
    :param max_speed: Distance travelled per second by a unit speed command.
    :param max_turn: Radians turned per second by a unit turn command.
    """

    name: str
    x: float
    y: float
    heading: float
    color: str
    radius: float = ROBOT_CONFIG.radius
    max_speed: float = ROBOT_CONFIG.max_speed
    max_turn: float = ROBOT_CONFIG.max_turn

    # Spatial queries

    def distance_to(self, other: Robot) -> float:
        """Return the Euclidean centre-to-centre distance to ``other``.

        :param other: Robot whose position is compared with this body.
        :return: Distance in arena units.
        """
        return hypot(other.x - self.x, other.y - self.y)

    def bearing_to(self, other: Robot) -> float:
        """Return the relative bearing from this heading to ``other``.

        Negative values place the other robot on the right and positive values
        place it on the left.

        :param other: Robot to locate.
        :return: Wrapped relative bearing in radians.
        """
        return wrap_angle(atan2(other.y - self.y, other.x - self.x) - self.heading)

    # Motion integration and steering

    def move(
        self,
        speed: float,
        turn: float,
        dt: float,
        bounds: tuple[float, float],
    ) -> None:
        """Advance the body and wrap it across arena boundaries.

        ``speed`` and ``turn`` are normalized commands scaled by
        :attr:`max_speed` and :attr:`max_turn`. The arena is toroidal: crossing
        one edge places the body at the corresponding point on the opposite
        edge without changing its heading.

        :param speed: Signed normalized linear command; negative moves backward.
        :param turn: Signed normalized angular command; positive turns left.
        :param dt: Simulation interval in seconds.
        :param bounds: Arena ``(width, height)`` in world units.
        """
        self.heading = wrap_angle(self.heading + self.max_turn * turn * dt)
        self.x += self.max_speed * speed * cos(self.heading) * dt
        self.y += self.max_speed * speed * sin(self.heading) * dt
        width, height = bounds
        self.x = wrap_coordinate(self.x, self.radius, width)
        self.y = wrap_coordinate(self.y, self.radius, height)

    def turn_towards(self, x: float, y: float) -> float:
        """Compute a normalized shortest-turn command toward a point.

        An angular error of 60 degrees or more saturates the command at one.

        :param x: Target horizontal position.
        :param y: Target vertical position.
        :return: Turn command in ``[-1, 1]``.
        """
        error = wrap_angle(atan2(y - self.y, x - self.x) - self.heading)
        return min(
            ROBOT_CONFIG.max_normalized_command,
            max(
                ROBOT_CONFIG.min_normalized_command,
                error / ROBOT_CONFIG.turn_saturation_angle,
            ),
        )
