from qrobot.bursts import ZeroBurst
from qrobot.models import AngularModel
from qrobot.qunits import QUnit
from qrobot import Roscore
from time import sleep


def test_qunit():
    roscore = Roscore()
    roscore.run()

    model = AngularModel(1, 1)
    burst = ZeroBurst()
    unit = QUnit("nome", model, burst, 0.1)

    unit.start()
    sleep(5)
    unit.stop()


if __name__ == "__main__":
    test_qunit()
