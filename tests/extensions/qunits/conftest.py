"""Shared fixtures discovered automatically by pytest for this directory.

Tests request these fixtures by name in their function arguments. Each fixture
is created again for each test; no explicit import is needed.
"""

from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from qrobot_qunits.base import BaseUnit


@pytest.fixture
def isolated(monkeypatch, caplog):
    """Return a Redis Mock and replace shared storage with local Python values.

    monkeypatch and caplog are built-in pytest fixtures. monkeypatch restores
    the original methods after the test; caplog restores the logging level.
    """
    # Preparing ordinary Python storage so constructing a unit starts no manager.
    monkeypatch.setattr(
        BaseUnit, "_shared_value", lambda self, code, value: SimpleNamespace(value=value)
    )
    # Enabling debug messages so tests also exercise the logging code.
    caplog.set_level("DEBUG")
    monkeypatch.setattr(BaseUnit, "_shared_list", lambda self, values: list(values))
    monkeypatch.setattr(BaseUnit, "_shared_dict", lambda self, values: dict(values))
    # Returning the same fake Redis client for all unit reads and writes.
    client = Mock()
    monkeypatch.setattr("qrobot_qunits.base.get_redis", Mock(return_value=client))
    return client


@pytest.fixture
def redis_runtime():
    """Provide Redis settings, a client, a cleanup list and a waiting helper.

    Tests append every created unit to the list before starting it. After the
    test, this fixture stops those units and closes their process managers and
    the Redis client. It never clears the whole database.
    """
    from time import monotonic, sleep
    from qrobot_qunits import RedisConfig
    from qrobot_qunits.redis import get_redis
    from redis.exceptions import ConnectionError

    # Connecting to the real test database; skipping if Redis is unavailable.
    config = RedisConfig(database=15)
    client = get_redis(config)
    try:
        client.ping()
    except ConnectionError:
        client.close()
        pytest.skip("Redis is not available on localhost:6379")
    # Tests add their units here so cleanup also runs after a failed assertion.
    units: list[BaseUnit] = []

    def wait_for(predicate):
        # Checking repeatedly because child processes finish at different times.
        deadline = monotonic() + 8
        while monotonic() < deadline:
            if predicate():
                return
            sleep(0.02)
        assert predicate(), "Worker did not publish the expected state within 8 seconds"

    try:
        # Handing these four values to the test until it finishes or fails.
        yield config, client, units, wait_for
    finally:
        try:
            # Stopping outputs before inputs, then releasing shared-storage processes.
            for unit in reversed(units):
                try:
                    unit.stop()
                finally:
                    manager = unit._multiproc_manager
                    if manager is not None:
                        manager.shutdown()
        finally:
            # Closing the test’s Redis connection after unit cleanup.
            client.close()
