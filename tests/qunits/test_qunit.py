from time import sleep

from qrobot import Core
from qrobot.qunits import QUnit
from qrobot.bursts import ZeroBurst
from qrobot.models import AngularModel


def test_qunit():

    Core().start()

    model = AngularModel(2, 10)
    burst = ZeroBurst()

    unit1 = QUnit("first_unit", model, burst, 1)
    unit2 = QUnit("second_unit", model, burst, 1)

    unit1.input(.6, 0)

    unit1.start()
    unit2.start()

    sleep(1)
    unit2.stop()

    sleep(1)
    unit1.query([0.1, 0.3])

    sleep(1)
    unit1.input(.7, 1)

    sleep(1)
    unit1.query([0.3, 0.2])

    Core().stop()


if __name__ == "__main__":
    test_qunit()
