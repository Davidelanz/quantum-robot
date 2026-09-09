"""Deterministic state transitions of the classical gripper."""

from dataclasses import replace

from qrobot_simulator.grasping_world.robots.classical_gripper import (
    ClassicalGripper,
    ClassicalGripperBrain,
)
from qrobot_simulator.grasping_world.robots.config import CLASSICAL_GRIPPER_CONFIG


def test_classical_gripper_requires_sustained_proximity() -> None:
    """Interrupted proximity evidence does not trigger a grasp."""
    gripper = ClassicalGripper(config=replace(CLASSICAL_GRIPPER_CONFIG, confirmation_time=0.3))
    assert isinstance(gripper.brain, ClassicalGripperBrain)
    near = {"proximity": 1.0, "touch": 1.0}
    far = {"proximity": 0.0, "touch": 1.0}

    # The far sample clears the first partial interval. Closing therefore needs
    # a fresh, continuous 0.3 seconds of near readings.
    assert gripper.command(near, 0.2) == 0.0
    assert gripper.command(far, 0.1) == 0.0
    assert gripper.command(near, 0.2) == 0.0
    assert gripper.command(near, 0.1) == 1.0


def test_classical_gripper_releases_failed_grasp() -> None:
    """An empty touch reading cancels a closing on the following update."""
    gripper = ClassicalGripper(config=replace(CLASSICAL_GRIPPER_CONFIG, confirmation_time=0.1))
    empty_near = {"proximity": 1.0, "touch": 1.0}

    # The first update requests closure. The following empty touch sample proves
    # that closure caught nothing and cancels the command.
    assert gripper.command(empty_near, 0.1) == 1.0
    assert gripper.command(empty_near, 0.1) == 0.0


def test_classical_gripper_holds_confirmed_grasp_for_configured_time() -> None:
    """A pressed touch switch keeps the jaws closed only for the hold interval."""
    gripper = ClassicalGripper(
        config=replace(CLASSICAL_GRIPPER_CONFIG, confirmation_time=0.1, grasp_time=0.3)
    )
    gripper.command({"proximity": 1.0, "touch": 1.0}, 0.1)

    # A pressed touch reading confirms the catch. The command remains closed
    # before the deadline and opens exactly when the holding time is reached.
    assert gripper.command({"proximity": 1.0, "touch": 0.0}, 0.2) == 1.0
    assert gripper.command({"proximity": 1.0, "touch": 0.0}, 0.1) == 0.0
