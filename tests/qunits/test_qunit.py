from qrobot.bursts import ZeroBurst
from qrobot.models import AngularModel
from qrobot.qunits import QUnit
from time import sleep


def test_qunit():
    model = AngularModel(2, 10)
    burst = ZeroBurst()

    unit1 = QUnit("first_unit", model, burst, 1)
    unit2 = QUnit("second_unit", model, burst, 1)

    unit1.input(.6, 0)
    

    unit1.start()
    unit2.start()
    sleep(2)
    unit2.stop()

    for _ in range(50):
        sleep(1)
        unit1.input(.7, 1)
    
if __name__ == "__main__":
    test_qunit()
