"""Tests for Redis actuator interfaces."""

from time import monotonic, sleep

import pytest
from redis.exceptions import ConnectionError

from qrobot_qunits import ActuatorUnit, RedisConfig, redis_utils
from qrobot_qunits.actuator import threshold_activation

TEST_REDIS_CONFIG = RedisConfig(database=15)


def test_actuator_threshold_is_strict_and_normalized():
    # Test that threshold_activation returns 1.0 when input is strictly above threshold
    assert threshold_activation(0.51, 0.5) == 1.0
    # Test that threshold_activation returns 0.0 when input equals threshold (strict comparison)
    assert threshold_activation(0.5, 0.5) == 0.0
    # Test that values outside normalized range [0, 1] raise ValueError
    with pytest.raises(ValueError):
        threshold_activation(1.1, 0.5)


@pytest.mark.redis
def test_actuator_reads_bursts_and_publishes_activation():
    # Initialize Redis client and check connection availability
    client = redis_utils.get_redis(TEST_REDIS_CONFIG)
    try:
        client.ping()
    except ConnectionError:
        pytest.skip("Redis is not available on localhost:6379")
    # Clear the test database to ensure clean state
    client.flushdb()
    # Pre-populate Redis with qUnit burst outputs that will drive the actuator
    client.mset({"p1 output": 1.0, "p2 output": 1.0})
    # Create an actuator that reads from two qUnits (p1, p2) with 0.5 threshold
    actuator = ActuatorUnit(
        "gripper",
        ["p1", "p2"],
        0.02,
        threshold=0.5,
        redis_config=TEST_REDIS_CONFIG,
    )
    try:
        # A non-normalozed input value falls back the default value
        client.set("p1 output", 1.1)
        assert actuator.input_vector == [0.0, 1.0]
        client.set("p1 output", 1.0)

        # Verify the input qUnits are correctly indexed for visualization
        assert actuator.in_qunits == {0: "p1", 1: "p2"}
        # Start the actuator background task
        actuator.start()
        # Wait up to 2 seconds for the actuator to process and publish activation
        deadline = monotonic() + 2
        while actuator.get_activation() != 1.0 and monotonic() < deadline:
            sleep(0.02)
        # Assert that activation reached 1.0 (both inputs at 1.0 > threshold of 0.5)
        assert actuator.get_activation() == 1.0
        # Verify that the normalized sum (input value) was correctly computed and stored
        input_value = client.get(actuator.id + " input")
        assert input_value is not None
        value = input_value.decode() if isinstance(input_value, bytes) else input_value
        assert float(value) == 1.0
    finally:
        # Clean up: stop the actuator background task
        actuator.stop()
        # Clean up: remove pre-populated test data from Redis
        client.delete("p1 output", "p2 output")

    # Verify that all actuator data was properly cleaned up from Redis
    assert redis_utils.redis_status(TEST_REDIS_CONFIG) == {}
