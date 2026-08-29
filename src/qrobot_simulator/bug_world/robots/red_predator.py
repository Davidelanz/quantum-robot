"""Red predator robot used by the bug-world ecosystem."""

from dataclasses import dataclass, field
from random import uniform

from .base import MotionMode, Robot
from .config import PREDATOR_CONFIG, ROBOT_CONFIG


@dataclass
class RedPredator(Robot):
    """Red robot that continuously steers toward a target.

    Random mode adds a slowly changing steering offset to the direct pursuit
    command; deterministic mode follows the shortest turn exactly.

    :param motion_mode: ``"deterministic"`` for direct pursuit or ``"random"``
        for pursuit with periodically sampled steering noise.
    :param bite_period: Minimum interval between scored predator bites, in seconds.
    """

    motion_mode: MotionMode = "deterministic"
    bite_period: float = PREDATOR_CONFIG.bite_period
    _noise: float = field(default=0.0, init=False, repr=False)
    _next_choice: float = field(default=0.0, init=False, repr=False)

    # Public simulation API

    def step(
        self,
        target: Robot,
        elapsed: float,
        dt: float,
        bounds: tuple[float, float],
    ) -> None:
        """Pursue ``target`` for one simulation interval.

        :param target: Body to chase.
        :param elapsed: Total simulation time in seconds.
        :param dt: Current simulation interval in seconds.
        :param bounds: Arena ``(width, height)`` in world units.
        """
        turn = self._pursuit_turn(target, elapsed)
        self.move(PREDATOR_CONFIG.pursuit_speed, turn, dt, bounds)

    # Internal pursuit policy

    def _pursuit_turn(self, target: Robot, elapsed: float) -> float:
        """Calculate clipped direct pursuit with optional steering noise."""
        if self.motion_mode == "random" and elapsed >= self._next_choice:
            self._noise = uniform(*PREDATOR_CONFIG.random_noise_range)
            self._next_choice = elapsed + uniform(*PREDATOR_CONFIG.random_choice_interval)
        noisy_turn = self.turn_towards(target.x, target.y) + self._noise
        return min(
            ROBOT_CONFIG.max_normalized_command,
            max(ROBOT_CONFIG.min_normalized_command, noisy_turn),
        )
