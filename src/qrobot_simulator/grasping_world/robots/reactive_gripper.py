"""Gripper that acts on the latest readings without temporal integration."""

from .base_gripper import BaseGripper, BaseGripperBrain, Diagnostics, Readings
from .config import REACTIVE_GRIPPER_CONFIG, ReactiveGripperConfig


class ReactiveGripperBrain(BaseGripperBrain):
    """Control the jaws from the current readings without remembering the past.

    A near proximity reading closes the open jaws immediately. Once closed,
    contact with a captured ball keeps them closed. They open when touch reports
    that the jaws are empty, either because nothing was caught or because the
    captured ball has been consumed.
    """

    def __init__(self, config: ReactiveGripperConfig) -> None:
        """Store thresholds and initialize an open command."""
        self.config = config
        self._activation = 0.0

    def start(self, readings: Readings) -> None:
        """Accept the common lifecycle call; no history needs initialization."""
        self._activation = 0.0

    @property
    def ready(self) -> bool:
        """Return true because the brain has no asynchronous workers."""
        return True

    def command(self, readings: Readings, dt: float) -> float:
        """Return a jaw command determined only by the current sensor sample."""
        if dt <= 0:
            raise ValueError("dt must be positive")
        if self._activation:
            # Touch is zero while prey is held. An empty closure or consumed
            # prey therefore makes the gripper open on the following update.
            self._activation = float(readings["touch"] <= self.config.contact_threshold)
        else:
            self._activation = float(readings["proximity"] >= self.config.proximity_threshold)
        return self._activation

    def stop(self) -> None:
        """Accept the common lifecycle call; no resources require cleanup."""

    def diagnostics(self) -> Diagnostics:
        """Expose the latest actuator decision for optional rendering."""
        return {"gripper_activation": self._activation}


class ReactiveGripper(BaseGripper):
    """Gripper that responds immediately without filtering sensor readings."""

    def __init__(
        self,
        config: ReactiveGripperConfig = REACTIVE_GRIPPER_CONFIG,
        brain: BaseGripperBrain | None = None,
    ) -> None:
        """Use the reactive brain unless a complete alternative is supplied."""
        selected_brain = brain if brain is not None else ReactiveGripperBrain(config)
        super().__init__(config, selected_brain)
