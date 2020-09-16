"""
    These functions are made to easily plot the specs of the device on which the software is running
"""

import os
import platform
import subprocess
import re
import multiprocessing
import pandas as pd
from IPython.display import display, HTML


def get_cpu_model(spec="model name"):
    if platform.system() == "Windows":
        return platform.processor()
    elif platform.system() == "Darwin":
        os.environ['PATH'] = os.environ['PATH'] + os.pathsep + '/usr/sbin'
        command = "sysctl -n machdep.cpu.brand_string"
        return subprocess.check_output(command).strip()
    elif platform.system() == "Linux":
        command = "cat /proc/cpuinfo"
        all_info = str(subprocess.check_output(command, shell=True).strip())
        all_info = all_info.split("\\n")
        for line in all_info:
            if spec in line:
                return re.sub(f".*{spec}.*: ", "", line, 1)
    return ""


def get_specs():
    table = [
        #["", platform.version()],
        ["Machine", platform.machine()],
        ["Platform", platform.platform()],
        ["Architecture", platform.architecture()],
        ["Cores", get_cpu_model("model name")],
        ["Number of cores", multiprocessing.cpu_count()],
        ["Python version", platform.python_version()],
    ]
    dataframe = pd.DataFrame(table, columns=["Spec", "Value"])
    display(HTML(dataframe.to_html(index=False)))
