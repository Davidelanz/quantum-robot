from qrobot import Roscore
from time import sleep

def test_roscore():
    roscore = Roscore()
    roscore.run()
    sleep(5)
    roscore.terminate()

if __name__ == "__main__":
    test_roscore()