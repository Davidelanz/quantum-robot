"""State, sensing, interactions, and construction of the bug-world ecosystem."""

from __future__ import annotations

from collections import Counter
from collections.abc import Callable
from dataclasses import dataclass, field
from math import degrees
from random import Random

from ..robots.base_robot import Robot
from ..robots.base_bug import BaseBug
from ..robots.blue_prey import BluePrey
from ..robots.classical_bug import ClassicalBug
from ..robots.config import (
    PREDATOR_CONFIG,
    PREY_CONFIG,
    PredatorConfig,
    PreyConfig,
)
from ..robots.red_predator import RedPredator
from ..utils.geometry import (
    contact_distance,
    farthest_point,
    heading_to_point,
    radius_safe_corners,
)
from ..utils.sensing import eye_response_strength
from .arena import Chessboard
from .config import WORLD_CONFIG, WorldConfig
from .factory import create_predator, create_prey
from .recording import BugRunRecord, BugWorldSample, capture_sample
from .runner import run_brain, run_controller, run_recorded_brain


@dataclass
class BugWorld:
    """Represent the bug, prey, predator, arena, sensors, and scores.

    :param board: Checkerboard containing every robot.
    :param bug: Classically or quantum-controlled bug body.
    :param prey: Blue prey population.
    :param predator: Red predator pursuing the bug.
    :param config: Arena, sensor, and contact configuration.
    :param elapsed: Total simulated time in seconds.
    :param readings: Latest bug sensor snapshot.
    :param bitten_prey: Number of prey bitten by the bug.
    :param predator_bites: Number of predator contacts scored against the bug.
    :param bug_biting: Whether the bug bite indicator is visible.
    :param predator_biting: Whether the predator bite indicator is visible.
    :param boundary_crossings: Cumulative crossings keyed by robot name.
    """

    board: Chessboard
    bug: BaseBug
    prey: list[BluePrey]
    predator: RedPredator
    config: WorldConfig = WORLD_CONFIG
    elapsed: float = 0.0
    readings: dict[str, float] = field(default_factory=dict)
    bitten_prey: int = 0
    predator_bites: int = 0
    bug_biting: bool = False
    predator_biting: bool = False
    boundary_crossings: Counter[str] = field(default_factory=Counter)
    _last_predator_bite: float = field(default=float("-inf"), init=False, repr=False)
    _bug_bite_cue_until: float = field(default=float("-inf"), init=False, repr=False)
    _predator_bite_cue_until: float = field(default=float("-inf"), init=False, repr=False)

    # Construction and world views

    @classmethod
    def demo(
        cls,
        bug: BaseBug | None = None,
        seed: int | None = None,
        config: WorldConfig = WORLD_CONFIG,
        prey_config: PreyConfig = PREY_CONFIG,
        predator_config: PredatorConfig = PREDATOR_CONFIG,
    ) -> BugWorld:
        """Create the configured demonstration ecosystem.

        :param bug: Existing controlled bug. A classical bug is created when omitted.
        :param seed: Optional seed controlling random prey and predator motion.
        :param config: Arena, population, sensor, and contact configuration.
        :param prey_config: Shared motion configuration for blue prey.
        :param predator_config: Motion and contact configuration for the predator.
        :returns: Initialized world with its first sensor snapshot.
        """
        rng = Random(seed)
        world = cls(
            Chessboard(config.board_columns, config.board_rows, config.board_cell_size),
            bug or ClassicalBug(),
            create_prey(config, prey_config, rng),
            create_predator(config, predator_config, rng),
            config,
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

    def run_headless(
        self,
        controller: Callable[[dict[str, float]], dict[str, float]],
        duration: float,
        dt: float = 0.01,
    ) -> Counter[str]:
        """Run a controller without constructing or refreshing a live view.

        Parameters
        ----------
        controller : callable
            Function mapping the latest readings to named actuator activations.
        duration : float
            Positive simulated duration in seconds.
        dt : float
            Positive fixed physics integration step in seconds.

        Returns
        -------
        collections.Counter
            Number of physics steps spent in each displayed behavior.
        """
        return run_controller(self, controller, duration, dt)

    def run_robot_headless(self, duration: float, dt: float = 0.01) -> Counter[str]:
        """Run any configured bug brain through the same headless world interface."""
        return run_brain(self, duration, dt)

    def run_recorded_headless(self, duration: float, dt: float = 0.01) -> BugRunRecord:
        """Run the configured brain and retain raw samples and discrete events."""
        return run_recorded_brain(self, duration, dt)

    def snapshot(self) -> BugWorldSample:
        """Capture one immutable record of the current simulation state."""
        return capture_sample(self)

    # Sensor calculation

    def sensor_readings(self) -> dict[str, float]:
        """Calculate the bug's proximity and stereo RGB sensor values.

        :returns: Normalized readings keyed by configured sensor name.
        """
        readings = {key: 0.0 for key in self.bug.config.sensor_keys}
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
            distance <= self.config.proximity_distance
            and abs(degrees(bearing)) <= self.config.proximity_half_angle_degrees
        ):
            readings["proximity"] = 1.0

        eye_rays = (("l", self.config.eye_angle), ("r", -self.config.eye_angle))
        for eye, ray_angle in eye_rays:
            channel = eye + color_channel
            response = eye_response_strength(distance, bearing, ray_angle, self.config)
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
            if prey.step((self.bug, self.predator), self.elapsed, dt, bounds):
                self.boundary_crossings[prey.name] += 1
        if self.predator.step(self.bug, self.elapsed, dt, bounds):
            self.boundary_crossings[self.predator.name] += 1
        if self.bug.apply_activations(activations, dt, bounds):
            self.boundary_crossings[self.bug.name] += 1

    def _process_bug_bites(self) -> None:
        """Score and respawn prey reached by an active bug bite."""
        if not self.bug.biting:
            return

        self._bug_bite_cue_until = self.elapsed + self.config.bite_cue_duration
        self.bug_biting = True
        for index, prey in enumerate(self.prey):
            bite_distance = contact_distance(self.bug, prey, self.config.bug_bite_reach)
            if self.bug.distance_to(prey) <= bite_distance:
                self._respawn_prey(index)
                self.bitten_prey += 1

    def _process_predator_bite(self) -> None:
        """Score predator contact when the predator's cooldown has completed."""
        bite_distance = contact_distance(
            self.bug,
            self.predator,
            self.config.predator_bite_reach,
        )
        touching = self.bug.distance_to(self.predator) <= bite_distance
        cooldown_complete = self.elapsed - self._last_predator_bite >= self.predator.bite_period
        if not touching or not cooldown_complete:
            return

        self.predator_bites += 1
        self._last_predator_bite = self.elapsed
        self._predator_bite_cue_until = self.elapsed + self.config.bite_cue_duration
        self.predator_biting = True

    def _respawn_prey(self, index: int) -> None:
        """Move captured prey to a farthest safe corner, facing the arena centre."""
        prey = self.prey[index]
        corners = radius_safe_corners(self.board.bounds, prey.radius)
        prey.x, prey.y = farthest_point((self.bug.x, self.bug.y), corners, index)
        width, height = self.board.bounds
        prey.heading = heading_to_point((prey.x, prey.y), (width / 2, height / 2))
