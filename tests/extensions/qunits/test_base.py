"""Unit tests for the shared qUnit worker lifecycle."""

from typing import cast
from unittest.mock import Mock

import pytest

from qrobot_qunits.base import BaseUnit

# monkeypatch is supplied by pytest and restores replacements after each test.
# StubUnit and _unit below are local helpers, not fixtures; they let these tests
# control worker behavior without starting real child processes.


class StubUnit(BaseUnit):
    """Concrete shell used to exercise BaseUnit without a process manager."""

    _clean_redis_mock: Mock
    _unit_task_mock: Mock

    def _clean_redis(self) -> None:
        self._clean_redis_mock()

    def _unit_task(self) -> None:
        self._unit_task_mock()


def _unit(process: Mock | None) -> StubUnit:
    """Build the lifecycle portion of a unit without starting a manager."""
    unit = object.__new__(StubUnit)
    unit.id = "test-unit"
    unit.redis_config = Mock()
    unit._logger = Mock()
    unit._stop_event = Mock()
    unit._loop_thread = process
    unit._clean_redis_mock = Mock()
    unit._unit_task_mock = Mock()
    return unit


def test_init():
    """Construction stores configuration without allocating a manager or worker."""
    # Preparing the unit and controlled inputs for this test.
    unit = StubUnit("test-unit", 0.1)
    # Checking the initial settings and values.
    assert unit.name == "test-unit"
    assert unit.id.startswith("test-unit-")
    assert unit.sampling_period == 0.1
    assert unit._loop_thread is None
    assert unit._multiproc_manager is None
    assert unit._worker_redis is None
    assert unit._published_redis_state == {}
    assert not unit._stop_event.is_set()


def test_getstate():
    """Pickling omits local process handles without mutating the parent."""
    # Preparing the unit and controlled inputs for this test.
    unit = _unit(Mock())
    unit._multiproc_manager = Mock()
    unit._worker_redis = Mock()
    # Preparing the state sent to a child process, without local process handles.
    state = unit.__getstate__()
    # Checking that only the copied state loses these handles.
    for name in ("_loop_thread", "_multiproc_manager", "_worker_redis"):
        assert state[name] is None
        assert getattr(unit, name) is not None
    # Checking that the unit identifier is preserved in the saved state.
    assert state["id"] == unit.id


def test_iter_and_repr():
    """The textual representation includes the unit's public configuration."""
    # Preparing the unit and controlled inputs for this test.
    unit = StubUnit("test-unit", 0.1)
    # Checking the dictionary and readable text describing this unit.
    assert dict(unit) == {"name": unit.name, "id": unit.id, "sampling_period": 0.1}
    assert repr(unit) == (
        f'StubUnit "{unit.id}"\n     name:\ttest-unit'
        f"\n     id:\t{unit.id}\n     sampling_period:\t0.1"
    )


def test_start_publishes_initial_state(monkeypatch: pytest.MonkeyPatch) -> None:
    """Starting a unit publishes and remembers fields available immediately."""
    # Preparing the unit and controlled inputs for this test.
    unit = StubUnit("test-unit", 0.1)
    unit._unit_task_mock = Mock()
    unit._clean_redis_mock = Mock()
    process = Mock()
    client = Mock()
    monkeypatch.setattr("qrobot_qunits.base.multiprocessing.Process", Mock(return_value=process))
    monkeypatch.setattr("qrobot_qunits.base.get_redis", Mock(return_value=client))

    # Starting the unit using the prepared process and Redis mocks.
    unit.start()

    # Checking that the worker starts and the initial class is written once.
    process.start.assert_called_once_with()
    client.mset.assert_called_once_with({f"{unit.id} class": "StubUnit"})
    assert unit._published_redis_state == {f"{unit.id} class": "StubUnit"}


def test_start_is_idempotent(monkeypatch):
    """Starting an already-live worker does not create another process."""
    # Preparing the unit and controlled inputs for this test.
    unit = _unit(Mock())
    process = unit._loop_thread
    assert process is not None
    cast(Mock, process).is_alive.return_value = True
    factory = Mock()
    monkeypatch.setattr("qrobot_qunits.base.multiprocessing.Process", factory)
    # Starting the unit using the prepared process and Redis mocks.
    unit.start()
    # Checking that a second start request creates no additional process.
    factory.assert_not_called()


def test_stop_signals_and_joins_before_cleanup(monkeypatch: pytest.MonkeyPatch) -> None:
    """A responsive worker is never terminated and its keys are removed."""
    # Preparing a fake worker whose running state is controlled by the test.
    process = Mock()
    process.is_alive.return_value = False
    unit = _unit(process)
    client = Mock()
    monkeypatch.setattr("qrobot_qunits.base.get_redis", Mock(return_value=client))

    # Stopping the unit and requesting cleanup of its Redis keys.
    unit.stop(timeout=0.25)

    # Checking that the worker is stopped and its Redis keys are removed.
    cast(Mock, unit._stop_event).set.assert_called_once_with()
    process.join.assert_called_once_with(0.25)
    process.terminate.assert_not_called()
    unit._clean_redis_mock.assert_called_once_with()
    client.delete.assert_called_once_with("test-unit class")
    assert unit._loop_thread is None


def test_stop_terminates_only_after_timeout(monkeypatch: pytest.MonkeyPatch) -> None:
    """An unresponsive worker receives the forced-stop fallback."""
    # Preparing a fake worker whose running state is controlled by the test.
    process = Mock()
    process.is_alive.return_value = True
    unit = _unit(process)
    monkeypatch.setattr("qrobot_qunits.base.get_redis", Mock(return_value=Mock()))

    # Stopping the unit and requesting cleanup of its Redis keys.
    unit.stop(timeout=0.1)

    # Checking that the worker is stopped and its Redis keys are removed.
    assert process.join.call_args_list[0].args == (0.1,)
    process.terminate.assert_called_once_with()
    assert process.join.call_args_list[1].args == ()
    unit._clean_redis_mock.assert_called_once_with()


def test_stop_reaps_abnormally_exited_worker(monkeypatch: pytest.MonkeyPatch) -> None:
    """Published keys from a crashed worker are cleaned when stop cleans it up."""
    # Preparing a fake worker whose running state is controlled by the test.
    process = Mock()
    process.is_alive.return_value = False
    process.exitcode = 1
    unit = _unit(process)
    client = Mock()
    monkeypatch.setattr("qrobot_qunits.base.get_redis", Mock(return_value=client))

    # Stopping the unit and requesting cleanup of its Redis keys.
    unit.stop()

    # Checking that the worker is stopped and its Redis keys are removed.
    unit._clean_redis_mock.assert_called_once_with()
    client.delete.assert_called_once_with("test-unit class")


def test_stop_rejects_negative_timeout() -> None:
    # Preparing the unit and controlled inputs for this test.
    unit = _unit(Mock())

    with pytest.raises(ValueError, match="timeout must not be negative"):
        unit.stop(timeout=-0.1)


def test_stop_before_start():
    """Stopping an idle unit does not attempt Redis cleanup."""
    # Preparing the unit and controlled inputs for this test.
    unit = _unit(None)
    # Requesting a stop even though no worker has been started.
    unit.stop()
    # Checking that an idle unit does not try to remove Redis keys.
    unit._clean_redis_mock.assert_not_called()


def test_loop_waits_until_next_period_deadline(monkeypatch: pytest.MonkeyPatch) -> None:
    """Task duration is subtracted from the wait between scheduled starts."""
    # Preparing the unit and controlled inputs for this test.
    unit = object.__new__(StubUnit)
    unit.logging_config = None
    unit.redis_config = Mock()
    unit.sampling_period = 0.2
    unit._unit_task_mock = Mock()
    stop_event = Mock()
    stop_event.is_set.side_effect = [False, True]
    unit._stop_event = stop_event
    client = Mock()
    monkeypatch.setattr("qrobot_qunits.base.get_redis", Mock(return_value=client))
    monkeypatch.setattr("qrobot_qunits.base.monotonic", Mock(side_effect=[10.0, 10.05]))

    # Running the loop with the prepared clock and stop signal.
    unit._loop()

    # Checking that a 0.05-second task leaves 0.15 seconds before the next sample.
    unit._unit_task_mock.assert_called_once_with()
    stop_event.wait.assert_called_once_with(pytest.approx(0.15))


def test_loop_skips_deadlines_missed_by_slow_task(monkeypatch: pytest.MonkeyPatch) -> None:
    """An overrun advances to the next future slot instead of busy-looping."""
    # Preparing the unit and controlled inputs for this test.
    unit = object.__new__(StubUnit)
    unit.logging_config = None
    unit.redis_config = Mock()
    unit.sampling_period = 0.2
    unit._unit_task_mock = Mock()
    unit._stop_event = Mock()
    unit._stop_event.is_set.side_effect = [False, True]
    monkeypatch.setattr("qrobot_qunits.base.get_redis", Mock(return_value=Mock()))
    monkeypatch.setattr("qrobot_qunits.base.monotonic", Mock(side_effect=[10.0, 10.55]))

    # Running the loop with the prepared clock and stop signal.
    unit._loop()

    # Checking that the next sample waits until 0.60 seconds, not a missed time.
    unit._stop_event.wait.assert_called_once_with(pytest.approx(0.05))


def test_loop_reuses_and_closes_worker_redis_client(monkeypatch: pytest.MonkeyPatch) -> None:
    """One Redis client serves the worker until its loop exits."""
    # Preparing the unit and controlled inputs for this test.
    unit = object.__new__(StubUnit)
    unit.logging_config = None
    unit.redis_config = Mock()
    unit.sampling_period = 0.2
    unit._stop_event = Mock()
    unit._stop_event.is_set.side_effect = [False, True]
    clients_used = []
    unit._unit_task_mock = Mock(side_effect=lambda: clients_used.append(unit._redis()))
    client = Mock()
    get_redis = Mock(return_value=client)
    monkeypatch.setattr("qrobot_qunits.base.get_redis", get_redis)

    # Running the loop with the prepared clock and stop signal.
    unit._loop()

    # Checking that one client handles the task and is closed when the loop ends.
    assert clients_used == [client]
    get_redis.assert_called_once_with(unit.redis_config)
    client.close.assert_called_once_with()
    assert unit._worker_redis is None


def test_loop_closes_client_on_task_failure(monkeypatch):
    """A failed task propagates after releasing the worker client."""
    # Preparing the unit and controlled inputs for this test.
    unit = _unit(None)
    unit.logging_config = Mock()
    unit.sampling_period = 0.1
    stop_event = Mock()
    stop_event.is_set.return_value = False
    unit._stop_event = stop_event
    unit._unit_task_mock.side_effect = RuntimeError("task failed")
    client = Mock()
    configure = Mock()
    monkeypatch.setattr("qrobot_qunits.base.configure_logging", configure)
    monkeypatch.setattr("qrobot_qunits.base.get_redis", Mock(return_value=client))
    with pytest.raises(RuntimeError, match="task failed"):
        unit._loop()
    # Checking that logging was configured and the failed task left no open client.
    configure.assert_called_once_with(unit.logging_config)
    client.close.assert_called_once_with()
    assert unit._worker_redis is None


def test_redis_parent_and_worker_clients(monkeypatch):
    """Parent calls obtain a client while worker calls reuse their connection."""
    # Preparing the unit and controlled inputs for this test.
    unit = _unit(None)
    factory = Mock()
    monkeypatch.setattr("qrobot_qunits.base.get_redis", factory)
    # Reading outside the worker first, then checking reuse of the worker client.
    assert unit._redis() is factory.return_value
    unit._worker_redis = Mock()
    assert unit._redis() is unit._worker_redis
    factory.assert_called_once_with(unit.redis_config)


def test_initial_redis_state():
    """The base startup state publishes the concrete unit type."""
    # Preparing the unit and controlled inputs for this test.
    unit = _unit(None)
    # Checking the information that will be written when the unit starts.
    assert unit._initial_redis_state() == {"test-unit class": "StubUnit"}


def test_redis_state_writer_sends_only_changed_fields() -> None:
    """One MSET contains new values while unchanged fields remain in Redis."""
    # Preparing the unit and controlled inputs for this test.
    unit = object.__new__(StubUnit)
    client = Mock()
    unit._worker_redis = client
    unit._published_redis_state = {"unit class": "StubUnit", "unit output": 0.5}

    # Writing the same state twice to check that unchanged values are not sent again.
    assert unit._write_changed_redis_state(
        {"unit class": "StubUnit", "unit output": 0.75, "unit state": "active"}
    )
    assert unit._write_changed_redis_state(
        {"unit class": "StubUnit", "unit output": 0.75, "unit state": "active"}
    )

    client.mset.assert_called_once_with({"unit output": 0.75, "unit state": "active"})
    assert unit._published_redis_state == {
        "unit class": "StubUnit",
        "unit output": 0.75,
        "unit state": "active",
    }


def test_failed_write_remains_pending():
    """Rejected publication is retried because the remembered values is unchanged."""
    # Preparing the unit and controlled inputs for this test.
    unit = _unit(None)
    unit._published_redis_state = {"output": 0.0}
    unit._worker_redis = Mock()
    unit._worker_redis.mset.side_effect = [False, True]
    # Checking that a rejected write keeps the old value, then retrying successfully.
    assert not unit._write_changed_redis_state({"output": 1.0})
    assert unit._published_redis_state == {"output": 0.0}
    assert unit._write_changed_redis_state({"output": 1.0})
    assert unit._published_redis_state == {"output": 1.0}
    assert unit._worker_redis.mset.call_count == 2


def test_shared_storage_reuses_lazy_manager(monkeypatch):
    """Scalars avoid a manager; lists and dictionaries share one lazy manager."""
    # Preparing the unit and controlled inputs for this test.
    unit = StubUnit("test-unit", 0.1)
    manager = Mock()
    factory = Mock(return_value=manager)
    monkeypatch.setattr("qrobot_qunits.base.multiprocessing.Manager", factory)
    scalar = unit._shared_value("d", 0.25)
    # Checking that a scalar needs no manager and both containers share one manager.
    assert scalar.value == 0.25
    factory.assert_not_called()
    assert unit._shared_list([1.0]) is manager.list.return_value
    assert unit._shared_dict({0: "source"}) is manager.dict.return_value
    factory.assert_called_once_with()
    manager.list.assert_called_once_with([1.0])
    manager.dict.assert_called_once_with({0: "source"})


@pytest.mark.parametrize("value, expected", [(0.01, 0.01), (1, 1.0)])
def test_period_check(value, expected):
    """The minimum period and larger numeric periods are accepted."""
    assert BaseUnit._period_check(value) == expected


@pytest.mark.parametrize(
    "value, error", [("0.1", TypeError), (None, TypeError), (0.009, ValueError)]
)
def test_period_check_rejects_invalid_values(value, error):
    """Non-numeric and too-short sampling periods fail validation."""
    with pytest.raises(error):
        BaseUnit._period_check(value)
