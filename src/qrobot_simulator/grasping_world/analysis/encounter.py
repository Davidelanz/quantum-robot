"""Reproducible motion and proximity disturbances for one grasping encounter."""

from dataclasses import dataclass
from random import Random


@dataclass(frozen=True)
class TimeInterval:
    """Represent one half-open interval in simulated seconds."""

    start: float
    duration: float

    def __post_init__(self) -> None:
        """Reject intervals that cannot occur in forward simulation time."""
        if self.start < 0 or self.duration <= 0:
            raise ValueError("interval start must be non-negative and duration positive")

    def contains(self, elapsed: float) -> bool:
        """Return whether ``elapsed`` lies in ``[start, start + duration)``."""
        return self.start <= elapsed < self.start + self.duration


@dataclass(frozen=True)
class MotionSegment:
    """Command one constant ball velocity for a simulated duration."""

    duration: float
    velocity: float

    def __post_init__(self) -> None:
        """Require every segment to advance simulated time."""
        if self.duration <= 0:
            raise ValueError("motion-segment duration must be positive")


@dataclass(frozen=True)
class ProximityDisturbance:
    """Configure repeatable noise, dropouts, and false-positive intervals.

    Dropouts and false positives replace the clean reading during their configured
    intervals. A dropout takes precedence if the two kinds of interval overlap.
    Gaussian noise is then added and the result is clipped to the sensor range.
    """

    noise_standard_deviation: float = 0.0
    dropouts: tuple[TimeInterval, ...] = ()
    false_positives: tuple[TimeInterval, ...] = ()

    def __post_init__(self) -> None:
        """Reject a negative Gaussian noise scale."""
        if self.noise_standard_deviation < 0:
            raise ValueError("noise standard deviation must be non-negative")

    def apply(self, value: float, elapsed: float, seed: int | None) -> float:
        """Return the disturbed value without retaining mutable random state."""
        if any(interval.contains(elapsed) for interval in self.dropouts):
            value = 0.0
        elif any(interval.contains(elapsed) for interval in self.false_positives):
            value = 1.0

        # Deriving a local generator from seed and time makes repeated reads of
        # one world state identical. Rendering or diagnostics therefore cannot
        # change the later noise sequence by reading a sensor an extra time.
        if self.noise_standard_deviation and seed is not None:
            generator = Random(f"{seed}:{elapsed.hex()}")
            value += generator.gauss(0.0, self.noise_standard_deviation)
        return min(1.0, max(0.0, value))


@dataclass(frozen=True)
class GraspingEncounter:
    """Define the exogenous inputs and ground truth of one paired encounter.

    ``motion`` is a sequence of constant-velocity segments. Negative velocity
    approaches the gripper and positive velocity moves away. ``opportunity`` is
    ground-truth metadata for experiment scoring; it does not alter the physics.
    """

    initial_distance: float
    motion: tuple[MotionSegment, ...]
    opportunity: TimeInterval | None
    disturbance: ProximityDisturbance = ProximityDisturbance()

    def __post_init__(self) -> None:
        """Require a physical initial distance and at least one motion segment."""
        if self.initial_distance < 0:
            raise ValueError("initial distance must be non-negative")
        if not self.motion:
            raise ValueError("an encounter needs at least one motion segment")
        if self.opportunity is not None:
            if self.opportunity.start >= self.duration:
                raise ValueError("opportunity must begin before the encounter ends")
            if self.opportunity.start + self.opportunity.duration > self.duration:
                raise ValueError("opportunity must end with the encounter")

    @property
    def duration(self) -> float:
        """Return the total simulated duration of all motion segments."""
        return sum(segment.duration for segment in self.motion)

    def velocity_at(self, elapsed: float) -> float:
        """Return the commanded velocity at one elapsed encounter time."""
        if elapsed < 0:
            raise ValueError("elapsed time must be non-negative")
        boundary = 0.0
        for segment in self.motion:
            boundary += segment.duration
            if elapsed < boundary:
                return segment.velocity
        return 0.0

    def next_motion_boundary(self, elapsed: float) -> float:
        """Return the end of the segment containing ``elapsed``.

        Returning the encounter duration after the scripted motion has finished
        lets the world integrate a physics step that crosses a segment boundary
        without making its trajectory depend on the chosen physics period.
        """
        if elapsed < 0:
            raise ValueError("elapsed time must be non-negative")
        boundary = 0.0
        for segment in self.motion:
            boundary += segment.duration
            if elapsed < boundary:
                return boundary
        return self.duration

    def is_valid_opportunity(self, elapsed: float) -> bool:
        """Return the declared grasp ground truth at ``elapsed``."""
        return self.opportunity is not None and self.opportunity.contains(elapsed)
