import subprocess
import shlex
import sys
import signal
import psutil
from .logs import get_logger

logger = get_logger(__file__)

def kill_child_processes(parent_pid, sig=signal.SIGTERM):
    try:
        parent = psutil.Process(parent_pid)
        logger.info(f"parent = {parent}")
    except psutil.NoSuchProcess:
        logger.error("parent process not existing")
        return
    children = parent.children(recursive=True)
    logger.info(f"children = {children}")
    for process in children:
        logger.info(f"trying to kill child: {str(process)}")
        process.send_signal(sig)

class Roscore(object):
    """
    roscore wrapped into a subprocess.
    Singleton implementation prevents from creating more than one instance.
    """
    __initialized = False
    def __init__(self):
        if Roscore.__initialized:
            raise Exception("You can't create more than 1 instance of Roscore.")
        Roscore.__initialized = True
    def run(self):
        try:
            self.roscore_process = subprocess.Popen(['roscore'])
            self.roscore_pid = self.roscore_process.pid  # pid of the roscore process (which has child processes)
        except OSError as e:
            sys.stderr.write('roscore could not be run')
            raise e
    def terminate(self):
        logger.info(f"try to kill child pids of roscore pid: {str(self.roscore_pid)}")
        kill_child_processes(self.roscore_pid)
        self.roscore_process.terminate()
        self.roscore_process.wait()  # important to prevent from zombie process
        Roscore.__initialized = False