"""
    These functions are made to easily plot the specs of the device on which the software is running
"""

import multiprocessing
import os
import platform
import re
import subprocess

import pandas as pd
from IPython.display import HTML, display


def get_cpu_model(spec="model name"):
    if platform.system() == "Windows":
        return platform.processor()
    if platform.system() == "Darwin":
        os.environ["PATH"] = os.environ["PATH"] + os.pathsep + "/usr/sbin"
        command = "sysctl -n machdep.cpu.brand_string"
        return subprocess.check_output(command).strip()
    if platform.system() == "Linux":
        command = "cat /proc/cpuinfo"
        stream = os.popen(command)
        all_info = stream.read()
        all_info.strip()
        all_info = all_info.split("\n")
        # all_info = str(subprocess.check_output(command, shell=True).strip())
        for line in all_info:
            if spec in line:
                return re.sub(f".*{spec}.*: ", "", line, 1)


def get_specs():
    table = [
        # ["", platform.version()],
        ["Machine", platform.machine()],
        ["Platform", platform.platform()],
        ["Architecture", platform.architecture()],
        ["Cores", get_cpu_model("model name")],
        ["Number of cores", multiprocessing.cpu_count()],
        ["Python version", platform.python_version()],
    ]
    dataframe = pd.DataFrame(table, columns=["Spec", "Value"])
    display(HTML(dataframe.to_html(index=False)))
