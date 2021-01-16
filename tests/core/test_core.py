from qrobot import Core
from time import sleep

if __name__ == "__main__":
    # Get the core
    core = Core()

    # Check if singleton works
    core2 = Core()
    assert core is core2

    # Stop before even start
    core.stop()

    # start and stop
    core.start()
    sleep(3)
    core.stop()

    # start
    sleep(3)
    core.start()
