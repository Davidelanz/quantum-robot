"""Shared gripper-to-brain interface used by the physical world."""

from qrobot_simulator.grasping_world.robots.base_gripper import BaseGripperBrain
from qrobot_simulator.grasping_world.robots.config import QuantumGripperConfig
from qrobot_simulator.grasping_world.robots.quantum_gripper import QuantumGripper


class FixedBrain(BaseGripperBrain):
    """Small test brain returning one fixed normalized action."""

    def __init__(self, activation: float) -> None:
        self.activation = activation
        self.latest_readings: dict[str, float] = {}

    def start(self, readings: dict[str, float]) -> None:
        self.latest_readings = readings.copy()

    @property
    def ready(self) -> bool:
        return True

    def command(self, readings: dict[str, float], dt: float) -> float:
        self.latest_readings = readings.copy()
        return self.activation

    def stop(self) -> None:
        return None

    def diagnostics(self) -> dict[str, float | None]:
        return {"fixed_activation": self.activation}


def test_quantum_gripper_accepts_a_complete_alternative_brain() -> None:
    """Brain injection bypasses qBrain construction while preserving world I/O."""
    brain = FixedBrain(0.8)
    gripper = QuantumGripper(config=QuantumGripperConfig(), brain=brain)
    readings = {"proximity": 0.4, "touch": 1.0}

    # The base class owns sensor/action delegation and physical thresholding;
    # neither the world nor QuantumGripper needs to know the brain internals.
    gripper.prepare_headless(readings)
    gripper.apply_activation(gripper.command(readings, 0.1))

    assert gripper.brain is brain
    assert brain.latest_readings == readings
    assert gripper.gripper_closed
    assert gripper.diagnostics() == {"fixed_activation": 0.8}
