from time import sleep

import pytest

import qrobot
from qrobot.bursts import ZeroBurst
from qrobot.models import AngularModel
from qrobot.qunits import QUnit


@pytest.mark.redistest
def test_qunit():
    # Layer 0
    l0_unit0 = QUnit(
        name="lo_unit0",
        model=AngularModel(n=2, tau=10),
        burst=ZeroBurst(),
        Ts=0.1,
        query=[0.1, 0.5],  # Query target initialized
        # No input
    )

    # Layer 1
    l1_unit0 = QUnit(
        name="l1_unit0",
        model=AngularModel(n=1, tau=3),
        burst=ZeroBurst(),
        Ts=1,
        in_qunits={0: l0_unit0.id},  # Will receive Input from l0_unit0, dim 0
    )

    l1_unit1 = QUnit(
        name="l1_unit1",
        model=AngularModel(n=1, tau=5),
        burst=ZeroBurst(),
        Ts=1,
        in_qunits={0: l0_unit0.id},  # Will receive input from l0_unit0, dim 1
    )

    print(l0_unit0)
    print(l1_unit0)
    print(l1_unit1)
    print(l0_unit0.in_qunits)
    print(l1_unit0.in_qunits)
    print(l1_unit1.in_qunits)

    l0_unit0.start()
    l1_unit0.start()
    l1_unit1.start()
    sleep(2)
    l0_unit0.stop()
    l1_unit0.stop()
    l1_unit1.stop()

    # Redis functions
    qrobot.qunits.redis_utils.redis_status()
    qrobot.qunits.redis_utils.flush_redis()


if __name__ == "__main__":
    test_qunit()
