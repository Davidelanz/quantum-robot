"""Randomly wandering ball prey presented to the gripper robot."""

from dataclasses import dataclass, field
from random import Random

from .config import BALL_PREY_CONFIG


@dataclass
class BallPrey:
    """Represent the moving ball and its one-dimensional wandering state.

    :param x: Horizontal display position in arena units.
    :param y: Vertical display position in arena units.
    :param distance: Distance from the ultrasonic sensor in centimetres.
    :param velocity: Signed velocity in centimetres per second.
    :param caught: Whether the gripper is currently holding the ball.
    :param radius: Display radius in arena units.
    :param color: Matplotlib-compatible display color.
    """

    x: float
    y: float
    distance: float
    velocity: float
    caught: bool = False
    radius: float = BALL_PREY_CONFIG.radius
    color: str = BALL_PREY_CONFIG.color
    _next_motion_change: float = field(default=0.0, init=False, repr=False)

    # Public motion API

    def step(
        self,
        elapsed: float,
        dt: float,
        minimum_distance: float,
        closed_barrier: float | None,
        rng: Random,
    ) -> None:
        """Advance a free ball and bounce it at physical boundaries.

        :param elapsed: Current simulation time in seconds.
        :param dt: Simulation interval in seconds.
        :param minimum_distance: Nearest permitted sensor distance.
        :param closed_barrier: Jaw boundary blocking entry, or ``None`` when open.
        :param rng: Random generator controlling motion changes.
        """
        if elapsed >= self._next_motion_change:
            self._change_motion(elapsed, rng)

        self.distance += self.velocity * dt
        lower_bound = max(minimum_distance, closed_barrier or minimum_distance)
        if self.distance < lower_bound:
            self.distance = lower_bound
            self.velocity = abs(self.velocity)
        elif self.distance > BALL_PREY_CONFIG.max_distance:
            self.distance = BALL_PREY_CONFIG.max_distance
            self.velocity = -abs(self.velocity)

    def schedule_motion_change(self, elapsed: float, rng: Random) -> None:
        """Schedule the next random velocity perturbation.

        :param elapsed: Current simulation time in seconds.
        :param rng: Random generator used to sample the interval.
        """
        self._next_motion_change = elapsed + rng.uniform(*BALL_PREY_CONFIG.motion_change_interval)

    # Internal motion policy

    def _change_motion(self, elapsed: float, rng: Random) -> None:
        """Perturb velocity without inspecting the ball position."""
        random_kick = rng.uniform(*BALL_PREY_CONFIG.velocity_kick_range)
        self.velocity = min(
            BALL_PREY_CONFIG.max_speed,
            max(-BALL_PREY_CONFIG.max_speed, self.velocity + random_kick),
        )
        self.schedule_motion_change(elapsed, rng)
