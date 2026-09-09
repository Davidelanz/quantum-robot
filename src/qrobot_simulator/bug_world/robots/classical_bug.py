"""Classical bug and its deterministic sensor-to-action brain."""

from .base_bug import Activations, BaseBug, BaseBugBrain, Diagnostics, Readings
from .config import CLASSICAL_BUG_CONFIG, ClassicalBugConfig


class ClassicalBugBrain(BaseBugBrain):
    """Recognize prey and threats before mapping them to bug actions.

    :param config: Thresholds and search activation of the controller.
    """

    def __init__(self, config: ClassicalBugConfig = CLASSICAL_BUG_CONFIG) -> None:
        """Initialize the explicit classical cognitive state."""
        self.config = config
        self._diagnostics: Diagnostics = {
            "prey_evidence": 0.0,
            "threat_evidence": 0.0,
        }

    def start(self, readings: Readings) -> None:
        """Initialize the semantic evidence from the first sensor snapshot."""
        self._update_evidence(readings)

    @property
    def ready(self) -> bool:
        """Return true because the classical controller is synchronous."""
        return True

    def command(self, readings: Readings, dt: float) -> Activations:
        """Convert stereo color and proximity readings into five actions."""
        if dt <= 0:
            raise ValueError("dt must be positive")
        prey, threat = self._update_evidence(readings)
        threshold = self.config.color_detection_threshold
        presence = readings["proximity"] >= self.config.proximity_threshold

        # The semantic evidence provides the classical counterpart of the two
        # cognitive qUnits: blue drives approach and red drives withdrawal.
        forward = prey if prey >= threshold else self.config.search_activation
        backward = threat if threat >= threshold else 0.0

        # Blue evidence turns toward prey, while red evidence turns away from a
        # threat. Opposing commands are combined by the common bug body.
        return {
            "bite": float(presence and prey >= threshold),
            "forward": forward,
            "backward": backward,
            "rotate_left": max(readings["lb"], readings["rr"]),
            "rotate_right": max(readings["rb"], readings["lr"]),
        }

    def stop(self) -> None:
        """Accept the shared lifecycle call; no resources require cleanup."""

    def diagnostics(self) -> Diagnostics:
        """Return the current deterministic semantic evidence."""
        return self._diagnostics.copy()

    def _update_evidence(self, readings: Readings) -> tuple[float, float]:
        """Store the strongest stereo blue and red responses."""
        prey = max(readings["lb"], readings["rb"])
        threat = max(readings["lr"], readings["rr"])
        self._diagnostics = {
            "prey_evidence": prey,
            "threat_evidence": threat,
        }
        return prey, threat


class ClassicalBug(BaseBug):
    """Physical bug driven by an injectable deterministic brain.

    :param config: Body and classical-controller configuration.
    :param brain: Complete alternative brain, or ``None`` for the default.
    """

    def __init__(
        self,
        config: ClassicalBugConfig = CLASSICAL_BUG_CONFIG,
        brain: BaseBugBrain | None = None,
    ) -> None:
        """Use the configured classical brain unless another brain is supplied."""
        selected_brain = brain if brain is not None else ClassicalBugBrain(config)
        super().__init__(config, selected_brain)
