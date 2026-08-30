"""Tests for Redis-connected sensorial units."""

from collections.abc import Generator
from time import monotonic, sleep

import pytest
from redis.exceptions import ConnectionError

from qrobot_qunits import RedisConfig, SensorialUnit
from qrobot_qunits.redis import get_redis, redis_status

TEST_REDIS_CONFIG = RedisConfig(database=15)


@pytest.fixture
def sensor() -> Generator[SensorialUnit, None, None]:
    unit = SensorialUnit(
        "distance",
        sampling_period=0.02,
        default_input=0.25,
        redis_config=TEST_REDIS_CONFIG,
    )
    yield unit
    if unit._loop_thread is not None and unit._loop_thread.is_alive():
        unit.stop()
    unit._multiproc_manager.shutdown()


def test_sensorial_initialization_and_input(sensor: SensorialUnit) -> None:
    assert dict(sensor) == {
        "name": "distance",
        "id": sensor.id,
        "sampling_period": 0.02,
    }

    sensor.scalar_reading = 0.75
    assert sensor.scalar_reading == 0.75

    # An out-of-range assignment falls back to the configured sensor input.
    sensor.scalar_reading = -0.01
    assert sensor.scalar_reading == 0.25


@pytest.mark.redis
def test_sensorial_publishes_and_cleans_up(sensor: SensorialUnit) -> None:
    client = get_redis(TEST_REDIS_CONFIG)
    try:
        client.ping()
    except ConnectionError:
        pytest.skip("Redis is not available on localhost:6379")
    client.flushdb()

    sensor.scalar_reading = 0.75
    try:
        sensor.start()
        deadline = monotonic() + 2
        while client.get(f"{sensor.id} output") is None and monotonic() < deadline:
            sleep(0.02)

        # The worker publishes the current scalar reading on its Redis output key.
        output = client.get(f"{sensor.id} output")
        assert output is not None
        assert float(output) == 0.75
    finally:
        sensor.stop()

    assert redis_status(TEST_REDIS_CONFIG) == {}
