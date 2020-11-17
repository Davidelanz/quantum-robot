from qrobot.bursts import ZeroBurst
from qrobot.models import AngularModel
from qrobot.qunits import QUnit
from qrobot import Roscore
from time import sleep


def test_qunit():
    model = AngularModel(1, 1)
    burst = ZeroBurst()

    unit1 = QUnit("first_unit", model, burst, 0.1)
    unit2 = QUnit("second_unit", model, burst, 0.1)

    unit1.load()
    unit2.load()
    
    unit1.start()
    unit2.start()

if __name__ == "__main__":
    test_qunit()
