"""QUnit behavior in source order, using isolated storage and Redis."""

import json
from unittest.mock import Mock

import pytest
import redis

from qrobot.bursts import ZeroBurst
from qrobot.models import AngularModel
from qrobot_qunits import QUnit
from qrobot_qunits.redis import RedisWriteError

# The isolated fixture comes from conftest.py in this directory. It replaces
# Redis with a Mock and shared storage with local values, lists and dictionaries.
# Tests can set its get/mget results and check which reads or writes were requested.


@pytest.fixture
def fixture_unit(isolated):
    """Prepare a two-input qUnit with two samples per window and defaults of 0.25 and 0.5."""
    # Pytest runs isolated first, then supplies this new unit to each test below.
    return QUnit(
        "processor",
        AngularModel(n=2, tau=2),
        ZeroBurst(),
        0.02,
        default_input=[0.25, 0.5],
        in_qunits={0: "sensor"},
    )


def test_init(isolated):
    """Omitted query, inputs and fallback start at zero and disconnected."""
    # Preparing the unit and controlled inputs for this test.
    unit = QUnit("processor", AngularModel(n=2, tau=2), ZeroBurst(), 0.02)
    # Checking the initial settings and values.
    assert unit.query == unit.default_input == [0.0, 0.0]
    assert unit.in_qunits == {0: None, 1: None}
    assert unit._t_idx.value == 0


@pytest.mark.parametrize("field", ["query", "default_input"])
def test_init_rejects_invalid_vectors(isolated, field):
    """Constructor vectors must match the model dimensions."""
    # Trying a one-value query or default input with a two-input model.
    with pytest.raises(ValueError):
        if field == "query":
            QUnit(
                "processor",
                AngularModel(n=2, tau=2),
                ZeroBurst(),
                0.02,
                query=[0.5],
            )
        else:
            QUnit(
                "processor",
                AngularModel(n=2, tau=2),
                ZeroBurst(),
                0.02,
                default_input=[0.5],
            )


def test_iter(fixture_unit):
    """Configuration describes the model, burst and current query."""
    # Reading the public settings and checking every value in source order.
    assert dict(fixture_unit) == {
        "name": fixture_unit.name,
        "id": fixture_unit.id,
        "model": str(fixture_unit.model),
        "burst": str(ZeroBurst),
        "query": [0.0, 0.0],
        "sampling_period": 0.02,
    }


@pytest.mark.parametrize("debug", [False, True])
def test_query(fixture_unit, debug):
    """Query updates are validated and callers receive a copy that can be changed separately."""
    # Preparing the same check with debug logging enabled and disabled.
    fixture_unit._logger = Mock()
    fixture_unit._logger.isEnabledFor.return_value = debug
    # Setting a query, reading its copy, and changing that copy.
    fixture_unit.query = [0.25, 0.75]
    result = fixture_unit.query
    result[0] = 1
    # Checking that changing the returned list leaves the stored query unchanged.
    assert fixture_unit.query == [0.25, 0.75]
    # Trying an invalid query and checking that the previous query is retained.
    with pytest.raises(ValueError):
        fixture_unit.query = [0.5]
    assert fixture_unit.query == [0.25, 0.75]


def test_in_qunits(fixture_unit):
    """Unconnected dimensions are explicit and returned mappings are separate copies."""
    # Reading the input connections into a separate dictionary.
    result = fixture_unit.in_qunits
    # Checking that the stored input connections have not changed.
    assert result == {0: "sensor", 1: None}
    result[0] = "other"
    assert fixture_unit.in_qunits[0] == "sensor"


def test_input_vector(fixture_unit, isolated):
    """Batch reads preserve dimensional order and keep the default inputs unchanged."""
    # Preparing two reads, each with a different missing input.
    fixture_unit.set_input(1, "other")
    isolated.mget.side_effect = [["0.75", None], [None, "0.9"]]
    # Reading the inputs and checking that missing values use the defaults.
    assert fixture_unit.input_vector == [0.75, 0.5]
    assert fixture_unit.input_vector == [0.25, 0.9]
    assert fixture_unit.default_input == [0.25, 0.5]
    isolated.mget.assert_called_with(["sensor output", "other output"])


@pytest.mark.parametrize(
    "value, expected",
    [
        (0, 0.0),
        (1, 1.0),
        ("0.75", 0.75),
        (None, 0.25),
        ("bad", 0.25),
        (-1, 0.25),
        (2, 0.25),
        (float("nan"), 0.25),
        (float("inf"), 0.25),
    ],
)
def test_normalize_input(fixture_unit, value, expected):
    """Malformed and out-of-range values use the dimension's fallback."""
    # Converting each input and checking invalid values use this input's default.
    assert fixture_unit._normalize_input(0, value) == expected


@pytest.mark.parametrize("debug", [False, True])
def test_set_input(fixture_unit, debug):
    """Changing an input connection changes only that dimension."""
    # Preparing the same check with debug logging enabled and disabled.
    fixture_unit._logger = Mock()
    fixture_unit._logger.isEnabledFor.return_value = debug
    fixture_unit.set_input(1, "new")
    # Checking the new input connection and rejecting a dimension that does not exist.
    assert fixture_unit.in_qunits == {0: "sensor", 1: "new"}
    with pytest.raises(IndexError):
        fixture_unit.set_input(2, "invalid")


def test_initial_redis_state(fixture_unit):
    """Startup information reflects the latest query and input connections."""
    # Preparing the unit and controlled inputs for this test.
    fixture_unit.query = [0.25, 0.75]
    # Checking the information that will be written when the unit starts.
    assert fixture_unit._initial_redis_state() == {
        f"{fixture_unit.id} class": "QUnit",
        f"{fixture_unit.id} query": "[0.25, 0.75]",
        f"{fixture_unit.id} in_qunits": json.dumps(fixture_unit.in_qunits),
    }


@pytest.mark.parametrize("stored, expected", [("0.75", 0.75), (None, None)])
def test_get_burst_output(fixture_unit, isolated, stored, expected):
    """Output lookup reads the known key, including an unpublished output."""
    # Preparing the values returned by the Redis mock.
    isolated.get.return_value = stored
    # Reading the result and checking that the correct output key is used.
    assert fixture_unit.get_burst_output() == expected
    isolated.get.assert_called_once_with(f"{fixture_unit.id} output")


def test_clean_redis(fixture_unit, isolated):
    """Cleanup removes all four processing fields."""
    # Requesting removal of the unit’s Redis keys.
    fixture_unit._clean_redis()
    # Checking that only the expected Redis keys are deleted.
    isolated.delete.assert_called_once_with(
        *(f"{fixture_unit.id} {key}" for key in ("output", "state", "query", "in_qunits"))
    )


@pytest.mark.parametrize("debug", [False, True])
def test_unit_task(fixture_unit, isolated, debug):
    """Samples accumulate until a full window is queried, published and reset."""
    # Preparing the same check with debug logging enabled and disabled.
    fixture_unit._logger = Mock()
    fixture_unit._logger.isEnabledFor.return_value = debug
    isolated.mget.return_value = ["0.75"]
    fixture_unit.model = Mock(tau=2, n=2)
    fixture_unit.model.decode.return_value = "decoded"
    fixture_unit.burst = Mock(return_value=0.8)
    fixture_unit._write_changed_redis_state = Mock(return_value=True)
    # Reading the first sample of a two-sample window.
    fixture_unit._unit_task()
    # Checking that an incomplete window produces no query or output.
    assert fixture_unit._t_idx.value == 1
    fixture_unit.model.query.assert_not_called()
    fixture_unit._write_changed_redis_state.assert_not_called()
    # Reading the second sample, which completes the window and produces an output.
    fixture_unit._unit_task()
    assert fixture_unit.model.encode_vector.call_count == 2
    fixture_unit.model.encode_vector.assert_called_with([0.75, 0.5])
    fixture_unit.model.query.assert_called_once_with([0.0, 0.0])
    fixture_unit.burst.assert_called_once_with("decoded")
    fixture_unit._write_changed_redis_state.assert_called_once_with(
        {
            f"{fixture_unit.id} output": 0.8,
            f"{fixture_unit.id} state": "decoded",
            f"{fixture_unit.id} query": "[0.0, 0.0]",
            f"{fixture_unit.id} in_qunits": json.dumps(fixture_unit.in_qunits),
        }
    )
    # Checking that processing starts a fresh window after the successful write.
    # Checking that processing starts a fresh window after the successful write.
    fixture_unit.model.clear.assert_called_once_with()
    assert fixture_unit._t_idx.value == 0


@pytest.mark.parametrize("failure", [False, redis.ConnectionError("offline")])
def test_unit_task_write_failure(fixture_unit, isolated, failure):
    """A failed publication raises without clearing the completed window."""
    # Preparing the values returned by the Redis mock.
    isolated.mget.return_value = [None]
    fixture_unit.model = Mock(tau=1, n=2)
    fixture_unit.burst = Mock(return_value=0.5)
    # Preparing either a rejected write or a Redis connection error.
    fixture_unit._write_changed_redis_state = Mock(return_value=failure)
    if isinstance(failure, Exception):
        fixture_unit._write_changed_redis_state.side_effect = failure
    # Running the update and checking that the write failure is reported.
    with pytest.raises(RedisWriteError):
        fixture_unit._unit_task()
    # Checking that a failed write leaves the completed window available.
    fixture_unit.model.clear.assert_not_called()
    assert fixture_unit._t_idx.value == 1
