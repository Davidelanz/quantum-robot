"""Blue prey robot used by the bug-world ecosystem."""

from dataclasses import dataclass, field
from random import uniform

from .base import MotionMode, Robot
from .config import PREY_CONFIG


@dataclass
class BluePrey(Robot):
    """Blue robot that wanders until a nearby hunter makes it flee.

    The deterministic mode follows a constant shallow arc. Random mode chooses
    a new turn command at irregular intervals. In both modes, a bug or predator
    closer than the configured flee distance takes priority and causes escape.

    :param motion_mode: ``"deterministic"`` for repeatable motion or
        ``"random"`` for periodically sampled wandering turns.

    """

    motion_mode: MotionMode = "deterministic"
    _wander_turn: float = field(default=PREY_CONFIG.initial_wander_turn, init=False, repr=False)
    _next_choice: float = field(default=0.0, init=False, repr=False)

    # Public simulation API

    def step(
        self,
        hunters: tuple[Robot, ...],
        elapsed: float,
        dt: float,
        bounds: tuple[float, float],
    ) -> None:
        """Select a wandering or escape command and advance the prey.

        :param hunters: Bodies from which the prey should flee.
        :param elapsed: Total simulation time in seconds.
        :param dt: Current simulation interval in seconds.
        :param bounds: Arena ``(width, height)`` in world units.
        """
        closest_hunter = min(hunters, key=self.distance_to)
        if self.distance_to(closest_hunter) < PREY_CONFIG.flee_distance:
            speed, turn = self._escape_command(closest_hunter)
        else:
            speed, turn = self._wander_command(elapsed)
        self.move(speed, turn, dt, bounds)

    # Internal movement policies

    def _escape_command(self, hunter: Robot) -> tuple[float, float]:
        """Calculate a full-speed command directed away from ``hunter``."""
        escape_x = 2 * self.x - hunter.x
        escape_y = 2 * self.y - hunter.y
        return PREY_CONFIG.flee_speed, self.turn_towards(escape_x, escape_y)

    def _wander_command(self, elapsed: float) -> tuple[float, float]:
        """Calculate the deterministic or randomly resampled wander command."""
        if self.motion_mode == "random" and elapsed >= self._next_choice:
            self._wander_turn = uniform(*PREY_CONFIG.random_turn_range)
            self._next_choice = elapsed + uniform(*PREY_CONFIG.random_choice_interval)
        turn = self._wander_turn if self.motion_mode == "random" else PREY_CONFIG.deterministic_turn
        return PREY_CONFIG.wander_speed, turn
