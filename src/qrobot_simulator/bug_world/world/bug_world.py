"""State, sensing, interactions, and construction of the bug-world ecosystem."""

from dataclasses import dataclass, field
from math import cos, degrees

from ..robots.base import Robot
from ..robots.blue_prey import BluePrey
from ..robots.bug_robot import BugRobot
from ..robots.config import PREDATOR_CONFIG, PREY_CONFIG, QBRAIN_CONFIG
from ..robots.red_predator import RedPredator
from ..utils.geometry import (
    contact_distance,
    farthest_point,
    heading_to_point,
    radius_safe_corners,
    wrap_angle,
)
from .config import WORLD_CONFIG


@dataclass(frozen=True)
class Chessboard:
    """Define the rectangular checkerboard arena.

    :param columns: Number of horizontal board cells.
    :param rows: Number of vertical board cells.
    :param cell_size: Width and height of one cell in world units.
    """

    columns: int = WORLD_CONFIG.board_columns
    rows: int = WORLD_CONFIG.board_rows
    cell_size: float = WORLD_CONFIG.board_cell_size

    @property
    def bounds(self) -> tuple[float, float]:
        """Return the arena dimensions.

        :returns: Arena ``(width, height)`` in world units.
        """
        return self.columns * self.cell_size, self.rows * self.cell_size


@dataclass
class BugWorld:
    """Represent the bug, prey, predator, arena, sensors, and scores.

    :param board: Checkerboard containing every robot.
    :param bug: qBrain-controlled bug body.
    :param prey: Blue prey population.
    :param predator: Red predator pursuing the bug.
    :param elapsed: Total simulated time in seconds.
    :param readings: Latest bug sensor snapshot.
    :param bitten_prey: Number of prey bitten by the bug.
    :param predator_bites: Number of predator contacts scored against the bug.
    :param bug_biting: Whether the bug bite indicator is visible.
    :param predator_biting: Whether the predator bite indicator is visible.
    """

    board: Chessboard
    bug: BugRobot
    prey: list[BluePrey]
    predator: RedPredator
    elapsed: float = 0.0
    readings: dict[str, float] = field(default_factory=dict)
    bitten_prey: int = 0
    predator_bites: int = 0
    bug_biting: bool = False
    predator_biting: bool = False
    _last_predator_bite: float = field(default=float("-inf"), init=False, repr=False)
    _bug_bite_cue_until: float = field(default=float("-inf"), init=False, repr=False)
    _predator_bite_cue_until: float = field(default=float("-inf"), init=False, repr=False)

    # Construction and world views

    @classmethod
    def demo(cls, bug: BugRobot | None = None) -> BugWorld:
        """Create the configured demonstration ecosystem.

        :param bug: Existing bug to place in the world. A brainless body is created
            when omitted.
        :returns: Initialized world with its first sensor snapshot.
        """
        world = cls(
            Chessboard(),
            bug or _create_bug_body(),
            _create_prey(),
            _create_predator(),
        )
        world.readings = world.sensor_readings()
        return world

    @property
    def robots(self) -> tuple[Robot, ...]:
        """Return all bodies in stable rendering order.

        :returns: Bug, prey, and predator bodies.
        """
        return (self.bug, *self.prey, self.predator)

    # Simulation update

    def step(self, activations: dict[str, float], dt: float) -> None:
        """Advance motion, interactions, and sensing by one interval.

        :param activations: Current actuator values for the bug.
        :param dt: Positive simulation interval in seconds.
        :raises ValueError: If ``dt`` is not positive.
        """
        if dt <= 0:
            raise ValueError("dt must be positive")

        self.elapsed += dt
        self._expire_bite_cues()
        self._move_robots(activations, dt)
        self._process_bug_bites()
        self._process_predator_bite()
        self.readings = self.sensor_readings()

    # Sensor calculation

    def sensor_readings(self) -> dict[str, float]:
        """Calculate the bug's proximity and stereo RGB sensor values.

        :returns: Normalized readings keyed by configured sensor name.
        """
        readings = {key: 0.0 for key in QBRAIN_CONFIG.sensor_keys}
        targets = tuple((prey, "b") for prey in self.prey) + ((self.predator, "r"),)
        for target, color_channel in targets:
            self._merge_target_readings(readings, target, color_channel)
        return readings

    def _merge_target_readings(
        self,
        readings: dict[str, float],
        target: Robot,
        color_channel: str,
    ) -> None:
        """Merge one visible animal into a sensor snapshot."""
        distance = self.bug.distance_to(target)
        bearing = self.bug.bearing_to(target)
        if (
            distance <= WORLD_CONFIG.proximity_distance
            and abs(degrees(bearing)) <= WORLD_CONFIG.proximity_half_angle_degrees
        ):
            readings["proximity"] = 1.0

        eye_rays = (("l", WORLD_CONFIG.eye_angle), ("r", -WORLD_CONFIG.eye_angle))
        for eye, ray_angle in eye_rays:
            channel = eye + color_channel
            response = eye_response_strength(distance, bearing, ray_angle)
            readings[channel] = max(readings[channel], response)

    # Motion and interaction internals

    def _expire_bite_cues(self) -> None:
        """Update visible bite indicators from their expiry times."""
        self.bug_biting = self.elapsed < self._bug_bite_cue_until
        self.predator_biting = self.elapsed < self._predator_bite_cue_until

    def _move_robots(self, activations: dict[str, float], dt: float) -> None:
        """Move prey, predator, and bug in the simulation's update order."""
        bounds = self.board.bounds
        for prey in self.prey:
            prey.step((self.bug, self.predator), self.elapsed, dt, bounds)
        self.predator.step(self.bug, self.elapsed, dt, bounds)
        self.bug.step(activations, dt, bounds)

    def _process_bug_bites(self) -> None:
        """Score and respawn prey reached by an active bug bite."""
        if not self.bug.biting:
            return

        self._bug_bite_cue_until = self.elapsed + WORLD_CONFIG.bite_cue_duration
        self.bug_biting = True
        for index, prey in enumerate(self.prey):
            bite_distance = contact_distance(self.bug, prey, WORLD_CONFIG.bug_bite_reach)
            if self.bug.distance_to(prey) <= bite_distance:
                self._respawn_prey(index)
                self.bitten_prey += 1

    def _process_predator_bite(self) -> None:
        """Score predator contact when the predator's cooldown has completed."""
        bite_distance = contact_distance(
            self.bug,
            self.predator,
            WORLD_CONFIG.predator_bite_reach,
        )
        touching = self.bug.distance_to(self.predator) <= bite_distance
        cooldown_complete = self.elapsed - self._last_predator_bite >= self.predator.bite_period
        if not touching or not cooldown_complete:
            return

        self.predator_bites += 1
        self._last_predator_bite = self.elapsed
        self._predator_bite_cue_until = self.elapsed + WORLD_CONFIG.bite_cue_duration
        self.predator_biting = True

    def _respawn_prey(self, index: int) -> None:
        """Move captured prey to a farthest safe corner, facing the arena centre."""
        prey = self.prey[index]
        corners = radius_safe_corners(self.board.bounds, prey.radius)
        prey.x, prey.y = farthest_point((self.bug.x, self.bug.y), corners, index)
        width, height = self.board.bounds
        prey.heading = heading_to_point((prey.x, prey.y), (width / 2, height / 2))


# Sensor response model


def eye_response_strength(distance: float, bearing: float, ray_angle: float) -> float:
    """Calculate the response of one configured bug-eye ray.

    :param distance: Centre distance from the bug to the observed target.
    :param bearing: Target bearing relative to the bug heading, in radians.
    :param ray_angle: Eye-ray offset from the bug heading, in radians.
    :returns: Normalized response in the interval ``[0, 1]``.
    """
    delta = abs(wrap_angle(bearing - ray_angle))
    angular_response = max(0.0, cos(delta)) ** WORLD_CONFIG.eye_angular_exponent
    distance_response = WORLD_CONFIG.eye_distance_scale / max(
        distance, WORLD_CONFIG.min_eye_distance
    )
    return min(1.0, angular_response * distance_response)


# Configured population factories


def _create_bug_body() -> BugRobot:
    """Create the simulated bug body without Redis processing units."""
    return BugRobot(connect_brain=False)


def _create_prey() -> list[BluePrey]:
    """Create the configured prey population."""
    return [
        BluePrey(
            name,
            x,
            y,
            heading,
            PREY_CONFIG.color,
            motion_mode=motion_mode,
        )
        for name, x, y, heading, motion_mode in WORLD_CONFIG.prey_spawns
    ]


def _create_predator() -> RedPredator:
    """Create the configured predator."""
    return RedPredator(
        *WORLD_CONFIG.predator_spawn,
        PREDATOR_CONFIG.color,
        max_speed=PREDATOR_CONFIG.max_speed,
        bite_period=PREDATOR_CONFIG.bite_period,
    )
