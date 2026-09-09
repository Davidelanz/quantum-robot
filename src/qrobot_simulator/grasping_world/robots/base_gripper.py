"""Shared physical and controller interfaces for grasping-world grippers."""

from abc import ABC, abstractmethod
from time import monotonic, sleep

from .config import BaseGripperConfig

Readings = dict[str, float]
Diagnostics = dict[str, float | None]


class BaseGripperBrain(ABC):
    """Translate common sensor readings into a normalized gripper action."""

    readiness_timeout: float = 7.0

    @abstractmethod
    def start(self, readings: Readings) -> None:
        """Initialize the controller with the first sensor snapshot."""

    @property
    @abstractmethod
    def ready(self) -> bool:
        """Return whether the controller can issue experimental commands."""

    @abstractmethod
    def command(self, readings: Readings, dt: float) -> float:
        """Consume readings and return one normalized actuator command."""

    @abstractmethod
    def stop(self) -> None:
        """Release resources owned by the controller."""

    @abstractmethod
    def diagnostics(self) -> Diagnostics:
        """Return optional values used by live diagnostic rendering."""

    def wait_until_ready(self, timeout: float) -> None:
        """Wait for asynchronous controller initialization to complete."""
        deadline = monotonic() + timeout
        while not self.ready:
            if monotonic() >= deadline:
                self.stop()
                raise RuntimeError("gripper brain did not become ready")
            sleep(0.01)


class BaseGripper:
    """Provide the physical interface used by the grasping world."""

    def __init__(self, config: BaseGripperConfig, brain: BaseGripperBrain) -> None:
        """Bind physical gripper configuration to an interchangeable brain."""
        self.config = config
        self.brain = brain
        self.gripper_closed = False

    @property
    def x(self) -> float:
        """Return the horizontal body position."""
        return self.config.x

    @property
    def y(self) -> float:
        """Return the vertical body position."""
        return self.config.y

    @property
    def color(self) -> str:
        """Return the body display color."""
        return self.config.color

    def apply_activation(self, activation: float) -> None:
        """Map a normalized brain action to the binary jaw state."""
        self.gripper_closed = activation > self.config.gripper_threshold

    def prepare_headless(self, readings: Readings, timeout: float | None = None) -> None:
        """Start the brain and exclude its initialization from experiment time."""
        self.brain.start(readings)
        self.brain.wait_until_ready(timeout or self.brain.readiness_timeout)

    def command(self, readings: Readings, dt: float) -> float:
        """Delegate one sensor-to-action update to the configured brain."""
        return self.brain.command(readings, dt)

    def stop(self) -> None:
        """Release resources owned by the configured brain."""
        self.brain.stop()

    def diagnostics(self) -> Diagnostics:
        """Return controller-specific values for optional rendering."""
        return self.brain.diagnostics()
