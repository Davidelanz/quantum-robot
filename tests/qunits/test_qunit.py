from time import sleep

from qrobot.qunits import QUnit
from qrobot.bursts import ZeroBurst
from qrobot.models import AngularModel


def test_qunit():

    model = AngularModel(n=2, tau=10)
    burst = ZeroBurst()

    # Layer 1
    l1_unit0 = QUnit(
        name="l1_unit0",
        model=model,
        burst=burst,
        Ts=0.01)
    # Will receive Input from l0_unit0, dim 0

    l1_unit1 = QUnit("l1_unit1", model, burst, 0.01)
    # Will receive input from l0_unit0, dim 1

    # Layer 0
    l0_unit0 = QUnit(
        "l0_unit0", model, burst, 0.01,
        query=[0.1, 0.5],  # Query target initialized
        out_qunits={
            l1_unit0: 0,  # Output in l1_unit0, dim 0
            l1_unit1: 1,  # Output in l1_unit1, dim 1
        }
    )

    l0_unit0.start()
    l1_unit0.start()
    l1_unit1.start()

    sleep(1)
    l0_unit0.set_input(.6, 0)
    sleep(3)

    l0_unit0.stop()
    l1_unit0.stop()
    l1_unit1.stop()


if __name__ == "__main__":
    test_qunit()
