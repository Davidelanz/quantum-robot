"""Tests for quantum bug construction and topology."""

from dataclasses import replace

import pytest
from redis.exceptions import ConnectionError

from qrobot_qunits import RedisConfig
from qrobot_qunits.redis import get_redis
from qrobot_simulator.bug_world.robots.config import QuantumBugConfig
from qrobot_simulator.bug_world.robots.quantum_bug import QuantumBugBrain


def test_direct_topology_connects_perception_to_actuators() -> None:
    """The direct comparison omits cognitive qUnits without changing its actions."""
    config = replace(QuantumBugConfig(), topology="direct")
    brain = QuantumBugBrain(RedisConfig(database=15), config=config)
    try:
        assert "prey" not in brain.qunits
        assert "threat" not in brain.qunits
        assert set(brain.actuators["forward"].in_qunits.values()) == {
            brain.qunits["left_blue"].id,
            brain.qunits["right_blue"].id,
        }
        assert set(brain.actuators["backward"].in_qunits.values()) == {
            brain.qunits["left_red"].id,
            brain.qunits["right_red"].id,
        }
    finally:
        # QUnit construction owns multiprocessing managers even before workers
        # start, so this structural test closes those managers explicitly.
        for unit in brain.qunits.values():
            if unit._multiproc_manager is not None:
                unit._multiproc_manager.shutdown()


def test_complete_qbrain_reaches_ready_state() -> None:
    """Every worker publishes output before the topology-aware startup deadline."""
    redis_config = RedisConfig(database=15)
    try:
        get_redis(redis_config).ping()
    except ConnectionError:
        pytest.skip("Redis integration service is unavailable")

    brain = QuantumBugBrain(redis_config)
    readings = {name: 0.0 for name in brain.sensors}
    try:
        brain.start(readings)
        brain.wait_until_ready(brain.readiness_timeout)
        assert brain.ready
    finally:
        brain.stop()
