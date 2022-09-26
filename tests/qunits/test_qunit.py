from time import sleep

import pytest

import qrobot
from qrobot.bursts import ZeroBurst
from qrobot.models import AngularModel
from qrobot.qunits import QUnit


@pytest.mark.redis
def test_qunit():

    # Layer 0
    l0_unit0 = QUnit(
        name="l0_unit0",
        model=AngularModel(n=2, tau=5),
        burst=ZeroBurst(),
        Ts=0.05,
        query=[0.1, 0.5],  # Query target initialized
        # No input
    )
    assert dict(l0_unit0) == {
        "name": "l0_unit0",
        "id": l0_unit0.id,
        "model": "[model: AngularModel, n: 2, tau: 5]",
        "burst": "<class 'qrobot.bursts.zeroburst.ZeroBurst'>",
        "query": [0.1, 0.5],
        "Ts": 0.05,
    }

    # Layer 1
    l1_unit0 = QUnit(
        name="l1_unit0",
        model=AngularModel(n=1, tau=3),
        burst=ZeroBurst(),
        Ts=0.2,
        in_qunits={0: l0_unit0.id},  # Will receive Input from l0_unit0, dim 0
    )
    assert dict(l1_unit0) == {
        "name": "l1_unit0",
        "id": l1_unit0.id,
        "model": "[model: AngularModel, n: 1, tau: 3]",
        "burst": "<class 'qrobot.bursts.zeroburst.ZeroBurst'>",
        "query": [0.0],
        "Ts": 0.2,
    }
    l1_unit1 = QUnit(
        name="l1_unit1",
        model=AngularModel(n=1, tau=5),
        burst=ZeroBurst(),
        Ts=0.2,
        in_qunits={0: l0_unit0.id},  # Will receive input from l0_unit0, dim 1
    )
    assert dict(l1_unit1) == {
        "name": "l1_unit1",
        "id": l1_unit1.id,
        "model": "[model: AngularModel, n: 1, tau: 5]",
        "burst": "<class 'qrobot.bursts.zeroburst.ZeroBurst'>",
        "query": [0.0],
        "Ts": 0.2,
    }

    # Check in_qunits
    assert l0_unit0.in_qunits == {0: None, 1: None}
    assert l1_unit0.in_qunits == {0: l0_unit0.id}
    assert l1_unit1.in_qunits == {0: l0_unit0.id}

    # Set new query state for l0_unit0
    assert l0_unit0.query == [0.1, 0.5]
    l0_unit0.query = [0.2, 0.4]
    assert l0_unit0.query == [0.2, 0.4]

    # Check the input vector
    assert l0_unit0.input_vector == [0.0, 0.0]
    assert l1_unit0.input_vector == [0.0]
    assert l1_unit1.input_vector == [0.0]

    # Start loops iterations (one temporal window each)
    l0_unit0._loop_iteration()
    l1_unit0._loop_iteration()
    l1_unit1._loop_iteration()
    # Then check that after some time the unit are writing something in redis
    assert l0_unit0.id in qrobot.qunits.redis_utils.redis_status()
    assert l1_unit0.id in qrobot.qunits.redis_utils.redis_status()
    assert l1_unit1.id in qrobot.qunits.redis_utils.redis_status()

    # Flush redis aftewards
    qrobot.qunits.redis_utils.flush_redis()
    assert qrobot.qunits.redis_utils.redis_status() == {}


if __name__ == "__main__":
    test_qunit()
