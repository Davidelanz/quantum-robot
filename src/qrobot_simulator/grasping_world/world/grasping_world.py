"""Physical encounter, sensors, interactions, and scoring for grasping."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from random import Random
from ..robots.ball_prey import BallPrey
from ..robots.base_gripper import BaseGripper
from ..robots.config import BALL_PREY_CONFIG, BallPreyConfig
from ..utils.sensors import proximity_reading, touch_reading
from .arena import GraspingArena
from .config import WORLD_CONFIG, GraspingWorldConfig

Controller = Callable[[dict[str, float]], float]


# Encounter state and dynamics


@dataclass
class GraspingWorld:
    """Represent one stationary gripper and one wandering ball prey.

    :param arena: Visible checkerboard dimensions.
    :param gripper: Classical or quantum gripper controlled by an actuator.
    :param ball: Ball prey moving in front of the gripper.
    :param elapsed: Simulated time in seconds.
    :param touch_pressed: Whether caught prey presses the touch sensor.
    :param readings: Latest normalized proximity and touch readings.
    :param correct_grips: Closing transitions that caught prey.
    :param missed_grips: Grippable visits that ended uncaught.
    :param empty_grips: Closing transitions made without grippable prey.
    :param consumed_prey: Captured prey held until consumption completed.
    :param premature_releases: Captured prey released before consumption completed.
    """

    arena: GraspingArena
    gripper: BaseGripper
    ball: BallPrey
    config: GraspingWorldConfig = WORLD_CONFIG
    prey_config: BallPreyConfig = BALL_PREY_CONFIG
    elapsed: float = 0.0
    touch_pressed: bool = False
    readings: dict[str, float] = field(default_factory=dict)
    correct_grips: int = 0
    missed_grips: int = 0
    empty_grips: int = 0
    consumed_prey: int = 0
    premature_releases: int = 0
    grip_response_times: list[float] = field(default_factory=list)
    _inside_visit: bool = False
    _visit_gripped: bool = False
    _consumption_started_at: float | None = None
    _visit_started_at: float | None = None
    _rng: Random = field(default_factory=Random, repr=False)

    # Construction and simulation API

    @classmethod
    def demo(
        cls,
        gripper: BaseGripper,
        seed: int | None = None,
        config: GraspingWorldConfig = WORLD_CONFIG,
        prey_config: BallPreyConfig = BALL_PREY_CONFIG,
        prey: BallPrey | None = None,
    ) -> GraspingWorld:
        """Create the configured arena, robot, and randomly placed ball prey.

        :param gripper: Configured gripper to place in the world.
        :param seed: Optional seed for reproducible prey movement.
        :param prey: Optional configured prey instance; otherwise one is sampled.
        :returns: Initialized world with its first sensor snapshot.
        """
        rng = Random(seed)
        ball = prey or BallPrey(
            0.0,
            gripper.y,
            rng.uniform(*prey_config.initial_distance_range),
            rng.uniform(*prey_config.initial_velocity_range),
            config=prey_config,
        )
        selected_prey_config = ball.config
        arena = GraspingArena(config.arena_width, config.arena_height, config.arena_cell_size)
        world = cls(arena, gripper, ball, config, selected_prey_config, _rng=rng)
        ball.schedule_motion_change(world.elapsed, rng)
        world._update_ball_position()
        world.readings = world.sensor_readings()
        return world

    def step(self, gripper_activation: float, dt: float) -> None:
        """Advance the encounter and apply the latest actuator output.

        :param gripper_activation: Normalized command applied to the jaws.
        :param dt: Positive interval in simulated seconds.
        :raises ValueError: If ``dt`` is not positive.
        """
        if dt <= 0:
            raise ValueError("dt must be positive")
        was_closed = self.gripper.gripper_closed
        ball_was_inside = self._ball_is_grippable()
        self.gripper.apply_activation(gripper_activation)
        self.elapsed += dt
        self._complete_consumption_if_due()
        self._handle_gripper_transition(was_closed, ball_was_inside)
        self._advance_ball(dt)
        self._update_visit_counter()
        self.touch_pressed = self.ball.caught
        self._update_ball_position()
        self.readings = self.sensor_readings()

    def run_headless(
        self,
        controller: Controller | None,
        duration: float,
        dt: float = 0.01,
    ) -> GraspingWorld:
        """Advance a controller without constructing or refreshing a live view.

        Parameters
        ----------
        controller : callable
            Function mapping the latest normalized readings to gripper activation.
        duration : float
            Positive simulated duration in seconds.
        dt : float
            Positive fixed physics integration step in seconds.

        Returns
        -------
        GraspingWorld
            This world after the requested simulated duration.
        """
        if duration <= 0 or dt <= 0:
            raise ValueError("duration and dt must be positive")
        target = self.elapsed + duration
        while self.elapsed < target:
            step_dt = min(dt, target - self.elapsed)
            readings = self.readings.copy()
            if controller is None:
                activation = self.gripper.command(readings, step_dt)
            else:
                activation = controller(readings)
            self.step(activation, step_dt)
        return self

    def run_robot_headless(self, duration: float, dt: float = 0.01) -> GraspingWorld:
        """Run either gripper through the same headless world interface."""
        if duration <= 0 or dt <= 0:
            raise ValueError("duration and dt must be positive")
        self.gripper.prepare_headless(self.readings)
        try:
            return self.run_headless(None, duration, dt)
        finally:
            self.gripper.stop()

    def sensor_readings(self) -> dict[str, float]:
        """Calculate the two normalized robot sensor values.

        :returns: Proximity and touch readings keyed by sensor name.
        """
        return {
            "proximity": (
                proximity_reading(
                    self.ball.distance, self.config.near_distance, self.config.far_distance
                )
                if self.ball.present
                else 0.0
            ),
            "touch": touch_reading(self.touch_pressed),
        }

    # Grip, consumption, release, and scoring internals

    def _handle_gripper_transition(self, was_closed: bool, ball_was_inside: bool) -> None:
        """Apply the physical consequence of a jaw-state transition."""
        if self.gripper.gripper_closed and not was_closed:
            if ball_was_inside:
                self._catch_ball()
            else:
                self.empty_grips += 1
        elif was_closed and not self.gripper.gripper_closed:
            if self.ball.caught:
                self._release_unconsumed_prey()
            elif not self.ball.present:
                self._respawn_ball()

    def _catch_ball(self) -> None:
        """Mark the prey caught and start its consumption interval."""
        self.correct_grips += 1
        self.ball.caught = True
        self._consumption_started_at = self.elapsed
        self._inside_visit = True
        self._visit_gripped = True
        if self._visit_started_at is not None:
            self.grip_response_times.append(self.elapsed - self._visit_started_at)

    def _advance_ball(self, dt: float) -> None:
        """Hold caught prey, wait while absent, or advance free prey."""
        if self.ball.caught:
            self.ball.velocity = 0.0
            return
        if not self.ball.present:
            return
        closed_barrier = self.config.grippable_distance if self.gripper.gripper_closed else None
        self.ball.step(
            self.elapsed,
            dt,
            self.config.minimum_distance,
            closed_barrier,
            self._rng,
            near_limit=self.config.grippable_distance,
        )

    def _complete_consumption_if_due(self) -> None:
        """Remove prey after uninterrupted contact for the configured interval."""
        if not self.ball.caught:
            return
        if self._consumption_started_at is None:
            raise RuntimeError("caught ball has no capture time")
        if self.elapsed - self._consumption_started_at < self.config.consumption_time:
            return

        # Disappearance removes contact but leaves the jaw command untouched.
        # The brain must observe the empty gripper and open it itself.
        self.ball.caught = False
        self.ball.present = False
        self.ball.velocity = 0.0
        self._consumption_started_at = None
        self.consumed_prey += 1

    def _release_unconsumed_prey(self) -> None:
        """Let prey escape when the robot opens before consumption completes."""
        self.ball.caught = False
        self._consumption_started_at = None
        self.premature_releases += 1
        self.ball.velocity = max(self.prey_config.escape_speed, abs(self.ball.velocity))

    def _respawn_ball(self) -> None:
        """Spawn new prey after consumed prey is absent and the jaws open."""
        self.ball.caught = False
        self.ball.present = True
        self._consumption_started_at = None
        self.ball.distance = self._rng.uniform(*self.prey_config.respawn_distance_range)
        self.ball.velocity = self._rng.uniform(*self.prey_config.initial_velocity_range)
        self._inside_visit = False
        self._visit_gripped = False
        self._visit_started_at = None
        self.ball.schedule_motion_change(self.elapsed, self._rng)

    def _update_visit_counter(self) -> None:
        """Count an uncaught visit when prey leaves the grippable zone."""
        is_inside = self._ball_is_grippable()
        if is_inside and not self._inside_visit:
            self._inside_visit = True
            self._visit_gripped = False
            self._visit_started_at = self.elapsed
        elif not is_inside and self._inside_visit:
            if not self._visit_gripped:
                self.missed_grips += 1
            self._inside_visit = False
            self._visit_gripped = False
            self._visit_started_at = None

    def _ball_is_grippable(self) -> bool:
        """Return whether prey lies inside the configured jaw interval."""
        return self.ball.present and (
            self.config.minimum_distance <= self.ball.distance <= self.config.grippable_distance
        )

    def _update_ball_position(self) -> None:
        """Convert sensor distance to the ball's horizontal display position."""
        sensor_origin_x = self.gripper.x + self.config.sensor_offset_x
        self.ball.x = sensor_origin_x + self.ball.distance * self.config.ball_distance_scale
        self.ball.y = self.gripper.y
