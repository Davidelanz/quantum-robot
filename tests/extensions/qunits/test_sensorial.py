"""Sensor behavior in source order; no Redis server or worker is started."""

from unittest.mock import Mock

import pytest
import redis

from qrobot_qunits import SensorialUnit
from qrobot_qunits.redis import RedisWriteError

# The isolated fixture comes from conftest.py in this directory. It replaces
# Redis with a Mock and shared storage with local values, lists and dictionaries.
# Tests can set its get/mget results and check which reads or writes were requested.


@pytest.fixture
def fixture_unit(isolated):
    """Prepare a sensor with an initial and default reading of 0.25."""
    # Pytest runs isolated first, then supplies this new unit to each test below.
    return SensorialUnit("distance", 0.02, default_input=0.25)


@pytest.mark.parametrize("default, expected", [(None, 0.0), (0.75, 0.75), (2, 0.0)])
def test_init(isolated, default, expected):
    """The initial reading uses a normalized default, or zero."""
    # Preparing the unit and controlled inputs for this test.
    unit = SensorialUnit("distance", 0.02, default_input=default)
    # Checking the initial settings and values.
    assert unit.default_input == unit.scalar_reading == expected


def test_iter(fixture_unit):
    """Configuration exposes the name, identifier and sampling period."""
    # Reading the public settings and checking every value in source order.
    assert dict(fixture_unit) == {
        "name": "distance",
        "id": fixture_unit.id,
        "sampling_period": 0.02,
    }


@pytest.mark.parametrize("debug", [False, True])
def test_scalar_reading(fixture_unit, debug):
    """A new reading replaces the shared scalar."""
    # Preparing the same check with debug logging enabled and disabled.
    fixture_unit._logger = Mock()
    fixture_unit._logger.isEnabledFor.return_value = debug
    fixture_unit.scalar_reading = 0.75
    # Reading back the newly assigned sensor value.
    assert fixture_unit.scalar_reading == 0.75


@pytest.mark.parametrize(
    "value, expected",
    [
        (0, 0.0),
        (1, 1.0),
        ("0.5", 0.5),
        (None, 0.25),
        ("bad", 0.25),
        (-0.1, 0.25),
        (1.1, 0.25),
        (float("nan"), 0.25),
        (float("inf"), 0.25),
    ],
)
def test_normalize_input(fixture_unit, value, expected):
    """Invalid readings fall back; normalized values include both endpoints."""
    # Checking the conversion directly, then through the reading setter.
    assert fixture_unit._normalize_input(value) == expected
    fixture_unit.scalar_reading = value
    assert fixture_unit.scalar_reading == expected


def test_clean_redis(fixture_unit, isolated):
    """Cleanup deletes only the sensor output."""
    # Requesting removal of the sensor output.
    fixture_unit._clean_redis()
    # Checking that only the expected Redis keys are deleted.
    isolated.delete.assert_called_once_with(f"{fixture_unit.id} output")


@pytest.mark.parametrize("debug", [False, True])
def test_unit_task(fixture_unit, debug):
    """One cycle publishes the current scalar."""
    # Preparing the same check with debug logging enabled and disabled.
    fixture_unit._logger = Mock()
    fixture_unit._logger.isEnabledFor.return_value = debug
    fixture_unit._write_changed_redis_state = Mock(return_value=True)
    # Running one sensor update.
    fixture_unit._unit_task()
    # Checking the values prepared for writing to Redis.
    fixture_unit._write_changed_redis_state.assert_called_once_with(
        {f"{fixture_unit.id} output": 0.25}
    )


@pytest.mark.parametrize("failure", [False, redis.ConnectionError("offline")])
def test_unit_task_write_failure(fixture_unit, failure):
    """Rejected writes and Redis errors become RedisWriteError."""
    # Preparing either a rejected write or a Redis connection error.
    fixture_unit._write_changed_redis_state = Mock(return_value=failure)
    if isinstance(failure, Exception):
        fixture_unit._write_changed_redis_state.side_effect = failure
    # Running the update and checking that the write failure is reported.
    with pytest.raises(RedisWriteError):
        fixture_unit._unit_task()
