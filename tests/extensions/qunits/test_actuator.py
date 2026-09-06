"""Actuator behavior in source order, without Redis or child processes."""

import json
from unittest.mock import Mock

import pytest
import redis

from qrobot_qunits import ActuatorUnit
from qrobot_qunits.actuator import threshold_activation
from qrobot_qunits.redis import RedisWriteError

# The isolated fixture comes from conftest.py in this directory. It replaces
# Redis with a Mock and shared storage with local values, lists and dictionaries.
# Tests can set its get/mget results and check which reads or writes were requested.


@pytest.fixture
def fixture_unit(isolated):
    """Prepare an actuator with two inputs, threshold 0.5 and default input 0.25."""
    # Pytest runs isolated first, then supplies this new unit to each test below.
    return ActuatorUnit("gripper", ["a", "b"], 0.02, default_input=0.25)


def test_init(isolated):
    """Inputs are copied and optional threshold and fallback use their defaults."""
    # Preparing the unit and controlled inputs for this test.
    inputs = ["a"]
    unit = ActuatorUnit("gripper", inputs, 0.02)
    inputs.append("b")
    # Checking the initial settings and values.
    assert unit.in_qunits == {0: "a"}
    assert unit.threshold == 0.5
    assert unit.default_input == 0.0


@pytest.mark.parametrize("inputs", [[], [1]])
def test_init_rejects_invalid_inputs(isolated, inputs):
    """At least one string input identifier is required."""
    # Trying an empty list and a list containing a value that is not an ID.
    with pytest.raises(ValueError, match="in_qunits"):
        ActuatorUnit("gripper", inputs, 0.02)


@pytest.mark.parametrize("field", ["threshold", "default_input"])
@pytest.mark.parametrize(
    "value, error", [("0.5", TypeError), (-0.1, ValueError), (1.1, ValueError)]
)
def test_init_rejects_invalid_configuration(isolated, field, value, error):
    """Threshold and fallback must be normalized scalar numbers."""
    # Trying invalid threshold and default input values during construction.
    with pytest.raises(error, match=field):
        ActuatorUnit("gripper", ["a"], 0.02, **{field: value})


def test_iter(fixture_unit):
    """Configuration includes input connections and activation threshold."""
    # Reading the public settings and checking every value in their source order.
    assert dict(fixture_unit) == {
        "name": "gripper",
        "id": fixture_unit.id,
        "in_qunits": {0: "a", 1: "b"},
        "threshold": 0.5,
        "sampling_period": 0.02,
    }


def test_in_qunits(fixture_unit):
    """Indexed input mappings are separate copies from the stored input connections."""
    # Reading the input connections into a separate dictionary.
    inputs = fixture_unit.in_qunits
    inputs[0] = "other"
    # Checking that the stored input connections have not changed.
    assert fixture_unit.in_qunits == {0: "a", 1: "b"}


def test_input_vector(fixture_unit, isolated):
    """A batch read preserves input order and substitutes missing values."""
    # Preparing the values returned by the Redis mock.
    isolated.mget.return_value = [None, "0.75"]
    # Reading the inputs and checking that missing values use the defaults.
    assert fixture_unit.input_vector == [0.25, 0.75]
    isolated.mget.assert_called_once_with(["a output", "b output"])


def test_normalized_sum(fixture_unit, isolated):
    """Activation uses the average of all inputs, including fallbacks."""
    # Preparing the values returned by the Redis mock.
    isolated.mget.return_value = [None, "0.75"]
    # Checking that the average includes the default for the missing input.
    assert fixture_unit.normalized_sum == 0.5


@pytest.mark.parametrize("value, expected", [(0.49, 0.0), (0.5, 0.0), (0.51, 1.0)])
def test_activation_for(fixture_unit, value, expected):
    """Only an average strictly above the configured threshold activates."""
    # Checking values below, equal to, and above the threshold.
    assert fixture_unit.activation_for(value) == expected


@pytest.mark.parametrize("stored, expected", [(None, None), ("1.0", 1.0)])
def test_get_activation(fixture_unit, isolated, stored, expected):
    """An unpublished activation is None; published values are floats."""
    # Preparing the values returned by the Redis mock.
    isolated.get.return_value = stored
    # Reading the result and checking that the correct output key is used.
    assert fixture_unit.get_activation() == expected
    isolated.get.assert_called_once_with(f"{fixture_unit.id} output")


def test_clean_redis(fixture_unit, isolated):
    """Cleanup removes the input average, output and input connections."""
    # Requesting removal of the unit’s Redis keys.
    fixture_unit._clean_redis()
    # Checking that only the expected Redis keys are deleted.
    isolated.delete.assert_called_once_with(
        *(f"{fixture_unit.id} {key}" for key in ("input", "output", "in_qunits"))
    )


def test_initial_redis_state(fixture_unit):
    """Startup publishes the actuator type and indexed input connections."""
    # Checking the values prepared before the worker process starts.
    assert fixture_unit._initial_redis_state() == {
        f"{fixture_unit.id} class": "ActuatorUnit",
        f"{fixture_unit.id} in_qunits": json.dumps(fixture_unit.in_qunits),
    }


def test_unit_task(fixture_unit, isolated):
    """One cycle publishes a consistent average, activation and input connections."""
    # Preparing the values returned by the Redis mock.
    isolated.mget.return_value = ["0.5", "1.0"]
    fixture_unit._write_changed_redis_state = Mock(return_value=True)
    # Running one processing step.
    fixture_unit._unit_task()
    # Checking the values prepared for writing to Redis.
    fixture_unit._write_changed_redis_state.assert_called_once_with(
        {
            f"{fixture_unit.id} input": 0.75,
            f"{fixture_unit.id} output": 1.0,
            f"{fixture_unit.id} in_qunits": json.dumps(fixture_unit.in_qunits),
        }
    )


@pytest.mark.parametrize("failure", [False, redis.ConnectionError("offline")])
def test_unit_task_write_failure(fixture_unit, isolated, failure):
    """Both rejected writes and Redis exceptions report RedisWriteError."""
    # Preparing the values returned by the Redis mock.
    isolated.mget.return_value = [None, None]
    # Preparing either a rejected write or a Redis connection error.
    fixture_unit._write_changed_redis_state = Mock(return_value=failure)
    if isinstance(failure, Exception):
        fixture_unit._write_changed_redis_state.side_effect = failure
    # Running the update and checking that the write failure is reported.
    with pytest.raises(RedisWriteError):
        fixture_unit._unit_task()


@pytest.mark.parametrize("value", [0, 0.5, 1])
def test_normalized_value(value):
    """Valid normalized numbers are converted to floats."""
    # Checking the lower bound, an inner value, and the upper bound.
    assert ActuatorUnit._normalized_value(value, "value") == float(value)


@pytest.mark.parametrize(
    "value, expected",
    [
        (0, 0.0),
        (1, 1.0),
        ("0.5", 0.5),
        (None, 0.25),
        ("bad", 0.25),
        (-1, 0.25),
        (2, 0.25),
        (float("nan"), 0.25),
        (float("inf"), 0.25),
    ],
)
def test_normalize_input(fixture_unit, value, expected):
    """Invalid input bursts use the configured fallback."""
    # Converting each input and checking invalid values use the default input.
    assert fixture_unit._normalize_input(value) == expected


@pytest.mark.parametrize(
    "value, threshold, expected", [(0, 0, 0.0), (1, 1, 0.0), (0.6, 0.5, 1.0), (0.4, 0.5, 0.0)]
)
def test_threshold_activation(value, threshold, expected):
    """The standalone activation rule uses a strict comparison."""
    # Comparing the input with the threshold and checking the binary output.
    assert threshold_activation(value, threshold) == expected


@pytest.mark.parametrize("value, threshold", [(1.1, 0.5), (0.5, -0.1)])
def test_threshold_activation_rejects_invalid_values(value, threshold):
    """Both arguments must be normalized."""
    # Trying an input or threshold outside the allowed zero-to-one range.
    with pytest.raises(ValueError):
        threshold_activation(value, threshold)
