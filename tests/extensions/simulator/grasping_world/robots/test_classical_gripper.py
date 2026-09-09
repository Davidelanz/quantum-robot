"""How recent proximity and touch readings control the classical gripper."""

from dataclasses import replace

import pytest

from qrobot_simulator.grasping_world.robots.classical_gripper import (
    ClassicalGripper,
    ClassicalGripperBrain,
    FixedWindowIntegrator,
)
from qrobot_simulator.grasping_world.robots.config import (
    CLASSICAL_GRIPPER_CONFIG,
    QUANTUM_GRIPPER_CONFIG,
)


def test_classical_and_quantum_grippers_use_equally_long_sensor_histories() -> None:
    """Both brains observe each sensor for the same amount of time."""
    assert CLASSICAL_GRIPPER_CONFIG.sampling_period == QUANTUM_GRIPPER_CONFIG.sampling_period
    assert CLASSICAL_GRIPPER_CONFIG.proximity_tau == QUANTUM_GRIPPER_CONFIG.proximity_tau
    assert CLASSICAL_GRIPPER_CONFIG.empty_gripper_tau == QUANTUM_GRIPPER_CONFIG.empty_gripper_tau


def test_sensor_average_changes_after_three_readings_are_collected() -> None:
    """The output remains unchanged until its configured group is complete."""
    integrator = FixedWindowIntegrator(sampling_period=0.1, window_size=3, initial_value=0.0)

    assert integrator.update(1.0, 0.2) == 0.0
    assert integrator.update(0.0, 0.1) == pytest.approx(2 / 3)


def test_sensor_reading_is_collected_only_at_the_configured_interval() -> None:
    """Physics updates between sampling times do not add extra readings."""
    integrator = FixedWindowIntegrator(sampling_period=0.1, window_size=2, initial_value=0.0)

    assert integrator.update(1.0, 0.05) == 0.0
    assert integrator.update(1.0, 0.05) == 0.0
    assert integrator.update(0.0, 0.1) == pytest.approx(0.5)


def test_classical_gripper_waits_for_three_near_readings_before_closing() -> None:
    """A brief near signal cannot immediately close the jaws."""
    config = replace(
        CLASSICAL_GRIPPER_CONFIG,
        sampling_period=0.1,
        proximity_tau=3,
        empty_gripper_tau=3,
    )
    gripper = ClassicalGripper(config)
    assert isinstance(gripper.brain, ClassicalGripperBrain)
    gripper.prepare_headless({"proximity": 0.0, "touch": 1.0})

    assert gripper.command({"proximity": 1.0, "touch": 1.0}, 0.2) == 0.0
    assert gripper.command({"proximity": 1.0, "touch": 1.0}, 0.1) == 1.0


def test_classical_gripper_opens_after_three_touch_readings_report_contact() -> None:
    """The longer touch average delays opening after contact begins."""
    config = replace(
        CLASSICAL_GRIPPER_CONFIG,
        sampling_period=0.1,
        proximity_tau=1,
        empty_gripper_tau=3,
    )
    gripper = ClassicalGripper(config)
    gripper.prepare_headless({"proximity": 1.0, "touch": 1.0})

    # The proximity mean changes immediately. The empty-gripper mean retains
    # its previous value until all three touch samples have been collected.
    assert gripper.command({"proximity": 1.0, "touch": 0.0}, 0.2) == 1.0
    assert gripper.command({"proximity": 1.0, "touch": 0.0}, 0.1) == 0.0
