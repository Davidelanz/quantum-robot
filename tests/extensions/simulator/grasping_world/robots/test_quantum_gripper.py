"""Quantum gripper and its colocated qBrain construction."""

from dataclasses import replace

import pytest

from qrobot_qunits import RedisConfig
from qrobot_simulator.grasping_world.robots.quantum_gripper import (
    QuantumGripper,
    QuantumGripperBrain,
)
from qrobot_simulator.grasping_world.robots.config import QUANTUM_GRIPPER_CONFIG


def test_quantum_gripper_builds_the_configured_qbrain() -> None:
    """Construction propagates temporal settings to both colocated qUnits."""
    # Use non-default values so the assertions prove that configuration reaches
    # the model and scheduler rather than merely restating package defaults.
    config = replace(
        QUANTUM_GRIPPER_CONFIG,
        sampling_period=0.2,
        proximity_tau=5,
        empty_gripper_tau=25,
    )
    gripper = QuantumGripper(RedisConfig(database=15), config=config)
    assert isinstance(gripper.brain, QuantumGripperBrain)
    brain = gripper.brain
    try:
        assert brain.qunits["proximity"].model.tau == 5
        assert brain.qunits["empty_gripper"].model.tau == 25
        assert brain.qunits["proximity"].sampling_period == pytest.approx(0.2)
    finally:
        # QUnit construction creates multiprocessing managers even though this
        # focused test does not start worker processes.
        for unit in brain.qunits.values():
            if unit._multiproc_manager is not None:
                unit._multiproc_manager.shutdown()
