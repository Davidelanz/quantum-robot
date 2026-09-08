"""Classical gripper and its deterministic sensor-to-action brain."""

from .base_gripper import BaseGripper, BaseGripperBrain, Diagnostics, Readings
from .config import CLASSICAL_GRIPPER_CONFIG, ClassicalGripperConfig


class ClassicalGripperBrain(BaseGripperBrain):
    """Close after sustained proximity and use touch to assess the grasp."""

    def __init__(self, config: ClassicalGripperConfig) -> None:
        """Initialize the controller timers in the open state."""
        self.config = config
        self._command_closed = False
        self._proximity_time = 0.0
        self._grasp_time = 0.0

    def start(self, readings: Readings) -> None:
        """Accept the common lifecycle call; no initialization is required."""

    @property
    def ready(self) -> bool:
        """Return true because this controller has no asynchronous workers."""
        return True

    def command(self, readings: Readings, dt: float) -> float:
        """Advance the timed controller and return open or closed activation."""
        if dt <= 0:
            raise ValueError("dt must be positive")

        # Touch distinguishes a confirmed catch from an empty closing. A catch
        # remains held for the configured time; an empty closing is cancelled.
        if self._command_closed:
            if readings["touch"] > 0.5:
                self._open()
            else:
                self._grasp_time += dt
                if self._grasp_time >= self.config.grasp_time:
                    self._open()
            return float(self._command_closed)

        # Interrupted proximity resets the evidence timer, so closing requires
        # one continuous interval above the configured threshold.
        if readings["proximity"] >= self.config.proximity_threshold:
            self._proximity_time += dt
        else:
            self._proximity_time = 0.0
        if self._proximity_time >= self.config.confirmation_time:
            self._command_closed = True
            self._proximity_time = 0.0
            self._grasp_time = 0.0
        return float(self._command_closed)

    def stop(self) -> None:
        """Accept the common lifecycle call; no resources require cleanup."""

    def diagnostics(self) -> Diagnostics:
        """Return no internal signals beyond the shared sensor readings."""
        return {}

    def _open(self) -> None:
        """Reset both timers when a grasp ends or fails."""
        self._command_closed = False
        self._proximity_time = 0.0
        self._grasp_time = 0.0


class ClassicalGripper(BaseGripper):
    """Physical gripper driven by an injectable classical brain."""

    def __init__(
        self,
        config: ClassicalGripperConfig = CLASSICAL_GRIPPER_CONFIG,
        brain: BaseGripperBrain | None = None,
    ) -> None:
        """Use the configured classical brain unless another brain is supplied."""
        selected_brain = brain if brain is not None else ClassicalGripperBrain(config)
        super().__init__(config, selected_brain)
