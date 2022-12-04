from time import sleep
from typing import Tuple

import pytest
import pytest_check as check

import qrobot
from qrobot.bursts import ZeroBurst
from qrobot.models import AngularModel
from qrobot.qunits import QUnit

# Using pytest_check for this test to allow the whole test
# to execute and stop the multithreading via unit.stop()
# methods instead of closing the main thread
# and leaving the unit subprocesses open.


def test_init_qunits() -> Tuple[QUnit, QUnit, QUnit]:
    # Layer 0
    l0_unit0 = QUnit(
        name="l0_unit0",
        model=AngularModel(n=2, tau=5),
        burst=ZeroBurst(),
        Ts=0.05,
        query=[0.1, 0.5],  # Query target initialized
        # No input
    )
    check.equal(
        dict(l0_unit0),
        {
            "name": "l0_unit0",
            "id": l0_unit0.id,
            "model": "[model: AngularModel, n: 2, tau: 5]",
            "burst": "<class 'qrobot.bursts.zeroburst.ZeroBurst'>",
            "query": [0.1, 0.5],
            "Ts": 0.05,
        },
    )

    # Layer 1
    l1_unit0 = QUnit(
        name="l1_unit0",
        model=AngularModel(n=1, tau=3),
        burst=ZeroBurst(),
        Ts=0.2,
        in_qunits={0: l0_unit0.id},  # Will receive Input from l0_unit0, dim 0
    )
    check.equal(
        dict(l1_unit0),
        {
            "name": "l1_unit0",
            "id": l1_unit0.id,
            "model": "[model: AngularModel, n: 1, tau: 3]",
            "burst": "<class 'qrobot.bursts.zeroburst.ZeroBurst'>",
            "query": [0.0],
            "Ts": 0.2,
        },
    )
    l1_unit1 = QUnit(
        name="l1_unit1",
        model=AngularModel(n=1, tau=5),
        burst=ZeroBurst(),
        Ts=0.2,
        in_qunits={0: l0_unit0.id},  # Will receive input from l0_unit0, dim 1
    )
    check.equal(
        dict(l1_unit1),
        {
            "name": "l1_unit1",
            "id": l1_unit1.id,
            "model": "[model: AngularModel, n: 1, tau: 5]",
            "burst": "<class 'qrobot.bursts.zeroburst.ZeroBurst'>",
            "query": [0.0],
            "Ts": 0.2,
        },
    )

    # Check in_qunits
    check.equal(l0_unit0.in_qunits, {0: None, 1: None})
    check.equal(l1_unit0.in_qunits, {0: l0_unit0.id})
    check.equal(l1_unit1.in_qunits, {0: l0_unit0.id})

    # Set new query state for l0_unit0
    check.equal(l0_unit0.query, [0.1, 0.5])
    l0_unit0.query = [0.2, 0.4]
    check.equal(l0_unit0.query, [0.2, 0.4])

    # Check the input vector
    check.equal(l0_unit0.input_vector, [0.0, 0.0])
    check.equal(l1_unit0.input_vector, [0.0])
    check.equal(l1_unit1.input_vector, [0.0])

    return l0_unit0, l1_unit0, l1_unit1


@pytest.mark.skip(
    reason="The test works running with VSCode debugger "
    "but not via pytest (the thread stops the _unit_task "
    "at the mode.decode() step)"
)
@pytest.mark.redis
def test_qunit():
    # Flush redis before starting
    qrobot.qunits.redis_utils.flush_redis()
    check.equal(qrobot.qunits.redis_utils.redis_status(), {})

    # Initialize qunits
    l0_unit0, l1_unit0, l1_unit1 = test_init_qunits()

    # Start unit tasks
    l0_unit0.start()
    l1_unit0.start()
    l1_unit1.start()

    # Process data for 4 seconds
    sleep(4)

    # Then check that after some time the unit are writing something in redis
    check.is_true(l0_unit0.id in qrobot.qunits.redis_utils.redis_status())
    check.is_true(l1_unit0.id in qrobot.qunits.redis_utils.redis_status())
    check.is_true(l1_unit1.id in qrobot.qunits.redis_utils.redis_status())

    # Stop unit tasks
    l0_unit0.stop()
    l1_unit0.stop()
    l1_unit1.stop()

    # Redis should be empty afterwards if the units stopped correctly
    check.equal(qrobot.qunits.redis_utils.redis_status(), {})
