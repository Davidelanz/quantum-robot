from time import monotonic, sleep
from typing import Tuple

import pytest
import pytest_check as check
from redis.exceptions import ConnectionError

from qrobot.bursts import ZeroBurst
from qrobot.models import AngularModel
from qrobot_qunits import QUnit, RedisConfig, SensorialUnit
from qrobot_qunits.redis import flush_redis, get_redis, redis_status

TEST_REDIS_CONFIG = RedisConfig(database=15)

# Soft assertions via pytest_check let the test reach its explicit
# worker cleanup even when an earlier expectation fails.


@pytest.fixture
def fixture_flush_redis() -> None:
    """Flush redis before starting the test."""
    try:
        get_redis(TEST_REDIS_CONFIG).ping()
    except ConnectionError:
        pytest.skip("Redis is not available on localhost:6379")
    flush_redis(TEST_REDIS_CONFIG)
    check.equal(redis_status(TEST_REDIS_CONFIG), {})


@pytest.fixture
def fixture_q_brain() -> Tuple[SensorialUnit, QUnit, QUnit]:
    """Initialize the qBrain."""
    # Layer 0
    l0_unit0 = SensorialUnit(name="l0_unit0", sampling_period=0.05, redis_config=TEST_REDIS_CONFIG)
    check.equal(
        dict(l0_unit0),
        {
            "name": "l0_unit0",
            "id": l0_unit0.id,
            "sampling_period": 0.05,
        },
    )
    # Layer 1
    l1_unit0 = QUnit(
        name="l1_unit0",
        model=AngularModel(n=1, tau=3),
        burst=ZeroBurst(),
        sampling_period=0.2,
        in_qunits={0: l0_unit0.id},  # Will receive Input from l0_unit0, dim 0
        redis_config=TEST_REDIS_CONFIG,
    )
    l1_unit1 = QUnit(
        name="l1_unit1",
        model=AngularModel(n=1, tau=5),
        burst=ZeroBurst(),
        sampling_period=0.2,
        in_qunits={0: l0_unit0.id},  # Will receive input from l0_unit0, dim 1
        redis_config=TEST_REDIS_CONFIG,
    )
    # Return qBrain
    q_brain = (l0_unit0, l1_unit0, l1_unit1)
    return q_brain


@pytest.mark.redis
def test_init_qunits(
    fixture_flush_redis,
    fixture_q_brain: Tuple[SensorialUnit, QUnit, QUnit],
) -> None:
    l0_unit0, l1_unit0, l1_unit1 = fixture_q_brain

    # Check qunits initialization
    check.equal(
        dict(l1_unit0),
        {
            "name": "l1_unit0",
            "id": l1_unit0.id,
            "model": "[model: AngularModel, n: 1, tau: 3]",
            "burst": "<class 'qrobot.bursts.zeroburst.ZeroBurst'>",
            "query": [0.0],
            "sampling_period": 0.2,
        },
    )
    check.equal(
        dict(l1_unit1),
        {
            "name": "l1_unit1",
            "id": l1_unit1.id,
            "model": "[model: AngularModel, n: 1, tau: 5]",
            "burst": "<class 'qrobot.bursts.zeroburst.ZeroBurst'>",
            "query": [0.0],
            "sampling_period": 0.2,
        },
    )

    # Check in_qunits
    check.equal(l1_unit0.in_qunits, {0: l0_unit0.id})
    check.equal(l1_unit1.in_qunits, {0: l0_unit0.id})

    # Set new query state for l1_unit0
    check.equal(l1_unit0.query, [0])
    l1_unit0.query = [0.2]
    check.equal(l1_unit0.query, [0.2])

    # Check the input vector
    check.equal(l1_unit0.input_vector, [0.0])
    check.equal(l1_unit1.input_vector, [0.0])

    # Redis values are applied to a new vector, never to the configured
    # fallback used by following temporal windows.
    input_vector = l1_unit0.input_vector
    input_vector[0] = 1.0
    check.equal(l1_unit0.default_input, [0.0])

    # A non-normalozed input value falls back the default value
    get_redis(TEST_REDIS_CONFIG).set(f"{l0_unit0.id} output", "1.01")
    check.equal(l1_unit0.input_vector, [0.0])


@pytest.mark.redis
def test_qunit(
    fixture_flush_redis,
    fixture_q_brain: Tuple[QUnit, QUnit, QUnit],
):
    """Worker processes publish outputs and clean their Redis keys on stop."""
    l0_unit0, l1_unit0, l1_unit1 = fixture_q_brain
    units = (l0_unit0, l1_unit0, l1_unit1)

    try:
        for unit in units:
            unit.start()

        expected_output_keys = {f"{unit.id} output" for unit in units}
        deadline = monotonic() + 6
        status = redis_status(TEST_REDIS_CONFIG)
        while monotonic() < deadline and not expected_output_keys.issubset(status):
            sleep(0.1)
            status = redis_status(TEST_REDIS_CONFIG)

        assert expected_output_keys.issubset(status)
        assert l1_unit0.get_burst_output() is not None
        assert l1_unit1.get_burst_output() is not None
        assert all(unit._loop_thread is not None and unit._loop_thread.is_alive() for unit in units)
    finally:
        for unit in units:
            unit.stop()

    assert redis_status(TEST_REDIS_CONFIG) == {}
