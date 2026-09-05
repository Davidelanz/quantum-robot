"""Unit tests for the shared qUnit worker lifecycle."""

from typing import cast
from unittest.mock import Mock

import pytest

from qrobot_qunits.base import BaseUnit


class StubUnit(BaseUnit):
    """Concrete shell used to exercise BaseUnit without a process manager."""

    _clean_redis_mock: Mock
    _unit_task_mock: Mock

    def _clean_redis(self) -> None:
        self._clean_redis_mock()

    def _unit_task(self) -> None:
        self._unit_task_mock()


def _unit(process: Mock) -> StubUnit:
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


def test_stop_signals_and_joins_before_cleanup(monkeypatch: pytest.MonkeyPatch) -> None:
    """A responsive worker is never terminated and its keys are removed."""
    process = Mock()
    process.is_alive.return_value = False
    unit = _unit(process)
    client = Mock()
    monkeypatch.setattr("qrobot_qunits.base.get_redis", Mock(return_value=client))

    unit.stop(timeout=0.25)

    cast(Mock, unit._stop_event).set.assert_called_once_with()
    process.join.assert_called_once_with(0.25)
    process.terminate.assert_not_called()
    unit._clean_redis_mock.assert_called_once_with()
    client.delete.assert_called_once_with("test-unit class")
    assert unit._loop_thread is None


def test_stop_terminates_only_after_timeout(monkeypatch: pytest.MonkeyPatch) -> None:
    """An unresponsive worker receives the forced-stop fallback."""
    process = Mock()
    process.is_alive.return_value = True
    unit = _unit(process)
    monkeypatch.setattr("qrobot_qunits.base.get_redis", Mock(return_value=Mock()))

    unit.stop(timeout=0.1)

    assert process.join.call_args_list[0].args == (0.1,)
    process.terminate.assert_called_once_with()
    assert process.join.call_args_list[1].args == ()
    unit._clean_redis_mock.assert_called_once_with()


def test_stop_reaps_abnormally_exited_worker(monkeypatch: pytest.MonkeyPatch) -> None:
    """Published keys from a crashed worker are cleaned when stop reaps it."""
    process = Mock()
    process.is_alive.return_value = False
    process.exitcode = 1
    unit = _unit(process)
    client = Mock()
    monkeypatch.setattr("qrobot_qunits.base.get_redis", Mock(return_value=client))

    unit.stop()

    unit._clean_redis_mock.assert_called_once_with()
    client.delete.assert_called_once_with("test-unit class")


def test_stop_rejects_negative_timeout() -> None:
    unit = _unit(Mock())

    with pytest.raises(ValueError, match="timeout must not be negative"):
        unit.stop(timeout=-0.1)


def test_loop_waits_on_stop_event_between_tasks(monkeypatch: pytest.MonkeyPatch) -> None:
    """The shared event replaces an uninterruptible sampling sleep."""
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

    unit._loop()

    unit._unit_task_mock.assert_called_once_with()
    stop_event.wait.assert_called_once_with(0.2)


def test_loop_reuses_and_closes_worker_redis_client(monkeypatch: pytest.MonkeyPatch) -> None:
    """One Redis client serves the worker until its loop exits."""
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

    unit._loop()

    assert clients_used == [client]
    get_redis.assert_called_once_with(unit.redis_config)
    client.close.assert_called_once_with()
    assert unit._worker_redis is None
