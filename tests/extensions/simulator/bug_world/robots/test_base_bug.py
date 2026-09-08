"""Tests for the common bug body and brain boundary."""

from qrobot_simulator.bug_world.robots.base_bug import BaseBugBrain
from qrobot_simulator.bug_world.robots.classical_bug import ClassicalBug
from qrobot_simulator.bug_world.robots.config import ClassicalBugConfig


class FixedBugBrain(BaseBugBrain):
    """Minimal injectable brain returning one fixed action mapping."""

    def __init__(self) -> None:
        self.started_with: dict[str, float] = {}
        self.stopped = False

    def start(self, readings: dict[str, float]) -> None:
        self.started_with = readings.copy()

    @property
    def ready(self) -> bool:
        return True

    def command(self, readings: dict[str, float], dt: float) -> dict[str, float]:
        return {"forward": 0.5, "rotate_left": 0.25}

    def stop(self) -> None:
        self.stopped = True

    def diagnostics(self) -> dict[str, float | None]:
        return {"fixed": 0.5}


def test_bug_accepts_an_alternative_brain_through_the_common_interface() -> None:
    """Injection changes cognition without requiring a different world-facing body."""
    brain = FixedBugBrain()
    bug = ClassicalBug(ClassicalBugConfig(), brain=brain)
    readings = {
        "proximity": 0.0,
        "lr": 0.0,
        "lg": 0.0,
        "lb": 0.0,
        "rr": 0.0,
        "rg": 0.0,
        "rb": 0.0,
    }

    # Startup, action production, diagnostics, and cleanup all pass through the
    # same interface that a quantum brain implements.
    bug.start(readings)
    activations = bug.command(readings, 0.1)
    bug.apply_activations(activations, 0.1, (10.0, 10.0))
    bug.stop()

    assert bug.brain is brain
    assert brain.started_with == readings
    assert bug.behavior == "FWD LEFT"
    assert bug.diagnostics() == {"fixed": 0.5}
    assert brain.stopped
