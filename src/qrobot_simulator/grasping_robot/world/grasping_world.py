"""Physical encounter, sensors, interactions, and scoring for grasping."""

from __future__ import annotations

from dataclasses import dataclass, field
from random import Random

from ..robots import BallPrey, GraspingRobot
from ..robots.config import BALL_PREY_CONFIG
from .config import WORLD_CONFIG

# Sensor interfaces


def proximity_interface(
    distance: float,
    near: float = WORLD_CONFIG.near_distance,
    far: float = WORLD_CONFIG.far_distance,
) -> float:
    """Map continuous distance to a normalized nearby-object signal.

    :param distance: Object distance in centimetres.
    :param near: Distance producing a full response.
    :param far: Distance producing a zero response.
    :returns: Normalized proximity in the interval ``[0, 1]``.
    :raises ValueError: If ``far`` is not greater than ``near``.
    """
    if far <= near:
        raise ValueError("far must be greater than near")
    return min(1.0, max(0.0, (far - distance) / (far - near)))


def touch_interface(pressed: bool) -> float:
    """Map the internal touch switch to the empty-gripper signal.

    :param pressed: Whether caught prey presses the switch.
    :returns: Zero when pressed and one while the gripper is empty.
    """
    return 0.0 if pressed else 1.0


# Arena geometry


@dataclass(frozen=True)
class GraspingArena:
    """Define the rectangular checkerboard arena.

    :param width: Arena width in display units.
    :param height: Arena height in display units.
    :param cell_size: Width and height of one checkerboard cell.
    """

    width: float = WORLD_CONFIG.arena_width
    height: float = WORLD_CONFIG.arena_height
    cell_size: float = WORLD_CONFIG.arena_cell_size

    @property
    def bounds(self) -> tuple[float, float]:
        """Return the arena dimensions.

        :returns: Arena ``(width, height)`` in display units.
        """
        return self.width, self.height


# Encounter state and dynamics


@dataclass
class GraspingWorld:
    """Represent one stationary gripper and one wandering ball prey.

    :param arena: Visible checkerboard dimensions.
    :param robot: Physical gripper body controlled by an actuator.
    :param ball: Ball prey moving in front of the gripper.
    :param elapsed: Simulated time in seconds.
    :param touch_pressed: Whether caught prey presses the touch sensor.
    :param readings: Latest normalized proximity and touch readings.
    :param correct_grips: Closing transitions that caught prey.
    :param missed_grips: Grippable visits that ended uncaught.
    :param empty_grips: Closing transitions made without grippable prey.
    """

    arena: GraspingArena
    robot: GraspingRobot
    ball: BallPrey
    elapsed: float = 0.0
    touch_pressed: bool = False
    readings: dict[str, float] = field(default_factory=dict)
    correct_grips: int = 0
    missed_grips: int = 0
    empty_grips: int = 0
    _inside_visit: bool = False
    _visit_gripped: bool = False
    _caught_at: float | None = None
    _rng: Random = field(default_factory=Random, repr=False)

    # Construction and simulation API

    @classmethod
    def demo(
        cls,
        robot: GraspingRobot | None = None,
        seed: int | None = None,
    ) -> GraspingWorld:
        """Create the configured arena, robot, and randomly placed ball prey.

        :param robot: Existing robot to place in the world. A brainless robot is
            created when omitted.
        :param seed: Optional seed for reproducible prey movement.
        :returns: Initialized world with its first sensor snapshot.
        """
        rng = Random(seed)
        robot = robot or GraspingRobot(connect_brain=False)
        ball = BallPrey(
            0.0,
            robot.y,
            rng.uniform(*BALL_PREY_CONFIG.initial_distance_range),
            rng.uniform(*BALL_PREY_CONFIG.initial_velocity_range),
        )
        world = cls(GraspingArena(), robot, ball, _rng=rng)
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
        was_closed = self.robot.gripper_closed
        ball_was_inside = self._ball_is_grippable()
        self.robot.apply_activation(gripper_activation)
        self.elapsed += dt
        self._handle_gripper_transition(was_closed, ball_was_inside)
        self._advance_ball(dt)
        self._update_visit_counter()
        self.touch_pressed = self.ball.caught
        self._update_ball_position()
        self.readings = self.sensor_readings()

    def sensor_readings(self) -> dict[str, float]:
        """Calculate the two normalized robot sensor values.

        :returns: Proximity and touch readings keyed by sensor name.
        """
        return {
            "proximity": proximity_interface(self.ball.distance),
            "touch": touch_interface(self.touch_pressed),
        }

    # Grip, digestion, and scoring internals

    def _handle_gripper_transition(self, was_closed: bool, ball_was_inside: bool) -> None:
        """Score and apply a newly issued closing command."""
        if self.robot.gripper_closed and not was_closed:
            if ball_was_inside:
                self._catch_ball()
            else:
                self.empty_grips += 1

    def _catch_ball(self) -> None:
        """Mark the ball caught and start the digestion interval."""
        self.correct_grips += 1
        self.ball.caught = True
        self._caught_at = self.elapsed
        self._inside_visit = True
        self._visit_gripped = True

    def _advance_ball(self, dt: float) -> None:
        """Hold caught prey or advance a free ball."""
        if self.ball.caught:
            self._hold_or_digest_ball()
            return
        closed_barrier = WORLD_CONFIG.grippable_distance if self.robot.gripper_closed else None
        self.ball.step(
            self.elapsed,
            dt,
            WORLD_CONFIG.minimum_distance,
            closed_barrier,
            self._rng,
        )

    def _hold_or_digest_ball(self) -> None:
        """Hold caught prey still and respawn it after digestion."""
        if self._caught_at is None:
            raise RuntimeError("caught ball has no capture time")
        if self.elapsed - self._caught_at >= WORLD_CONFIG.digestion_time:
            self._respawn_ball()
        else:
            self.robot.gripper_closed = True
            self.ball.velocity = 0.0

    def _respawn_ball(self) -> None:
        """Replace eaten prey at a random far position."""
        self.ball.caught = False
        self._caught_at = None
        self.ball.distance = self._rng.uniform(*BALL_PREY_CONFIG.respawn_distance_range)
        self.ball.velocity = self._rng.uniform(*BALL_PREY_CONFIG.initial_velocity_range)
        self._inside_visit = False
        self._visit_gripped = False
        self.ball.schedule_motion_change(self.elapsed, self._rng)

    def _update_visit_counter(self) -> None:
        """Count an uncaught visit when prey leaves the grippable zone."""
        is_inside = self._ball_is_grippable()
        if is_inside and not self._inside_visit:
            self._inside_visit = True
            self._visit_gripped = False
        elif not is_inside and self._inside_visit:
            if not self._visit_gripped:
                self.missed_grips += 1
            self._inside_visit = False
            self._visit_gripped = False

    def _ball_is_grippable(self) -> bool:
        """Return whether prey lies inside the configured jaw interval."""
        return (
            WORLD_CONFIG.minimum_distance <= self.ball.distance <= WORLD_CONFIG.grippable_distance
        )

    def _update_ball_position(self) -> None:
        """Convert sensor distance to the ball's horizontal display position."""
        sensor_origin_x = self.robot.x + WORLD_CONFIG.sensor_offset_x
        self.ball.x = sensor_origin_x + self.ball.distance * WORLD_CONFIG.ball_distance_scale
        self.ball.y = self.robot.y
