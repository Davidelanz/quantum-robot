"""Shared body and controller interfaces for classical and quantum bugs."""

from abc import ABC, abstractmethod
from time import monotonic, sleep

from ..utils.actions import behavior_label, motion_commands
from .base_robot import Robot
from .config import BaseBugConfig

Readings = dict[str, float]
Activations = dict[str, float]
Diagnostics = dict[str, float | None]


class BaseBugBrain(ABC):
    """Translate common bug sensors into normalized actuator values.

    :ivar readiness_timeout: Maximum wall-clock seconds allowed for startup.
    """

    readiness_timeout: float = 7.0

    @abstractmethod
    def start(self, readings: Readings) -> None:
        """Initialize the controller from the first sensor snapshot."""

    @property
    @abstractmethod
    def ready(self) -> bool:
        """Return whether the controller can issue commands."""

    @abstractmethod
    def command(self, readings: Readings, dt: float) -> Activations:
        """Consume one sensor snapshot and return actuator activations."""

    @abstractmethod
    def stop(self) -> None:
        """Release resources owned by the controller."""

    @abstractmethod
    def diagnostics(self) -> Diagnostics:
        """Return optional internal values for recording and rendering."""

    def wait_until_ready(self, timeout: float) -> None:
        """Wait for an asynchronous controller to publish its first output."""
        deadline = monotonic() + timeout
        while not self.ready:
            if monotonic() >= deadline:
                self.stop()
                raise RuntimeError("bug brain did not become ready")
            sleep(0.01)


class BaseBug(Robot):
    """Provide the body and action interface used by the bug world.

    :param config: Shared body and action-mapping configuration.
    :param brain: Controller implementing the common lifecycle.
    :ivar behavior: Current human-readable action label.
    :ivar biting: Whether the bite action is currently active.
    """

    def __init__(self, config: BaseBugConfig, brain: BaseBugBrain) -> None:
        """Bind an interchangeable brain to the configured physical body."""
        super().__init__(
            config.name,
            config.start_x,
            config.start_y,
            config.start_heading,
            config.color,
            radius=config.radius,
            max_speed=config.max_speed,
            max_turn=config.max_turn,
        )
        self.config = config
        self.brain = brain
        self.behavior = "SEARCH"
        self.biting = False

    def start(self, readings: Readings, timeout: float | None = None) -> None:
        """Start the brain and wait until it can issue commands."""
        self.brain.start(readings)
        self.brain.wait_until_ready(timeout or self.brain.readiness_timeout)

    def command(self, readings: Readings, dt: float) -> Activations:
        """Delegate one sensor-to-action update to the configured brain."""
        return self.brain.command(readings, dt)

    def apply_activations(
        self, activations: Activations, dt: float, bounds: tuple[float, float]
    ) -> bool:
        """Interpret normalized actuator values and advance the body."""
        speed, turn, self.biting = motion_commands(activations, self.config)
        forward = activations.get("forward", 0.0)
        self.behavior = behavior_label(speed, turn, forward, self.biting)
        return self.move(speed, turn, dt, bounds)

    def stop(self) -> None:
        """Release resources owned by the configured brain."""
        self.brain.stop()

    def diagnostics(self) -> Diagnostics:
        """Return controller-specific values through the common interface."""
        return self.brain.diagnostics()
