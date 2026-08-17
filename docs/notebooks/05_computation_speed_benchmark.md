---
jupytext:
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.19.5
kernelspec:
  display_name: Python 3 (ipykernel)
  language: python
  name: python3
---

# Computation speed benchmark

+++

In this notebook, we tested the average computation speed for various models in different cases.

```{code-cell} ipython3
import multiprocessing
import os
import platform
import re
import subprocess
import time

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from IPython.display import HTML, display
```

## Local machine details

Log the local machine details on which the test is carried out:

```{code-cell} ipython3
def get_cpu_model(spec="model name"):
    if platform.system() == "Windows":
        return platform.processor()
    if platform.system() == "Darwin":
        try:
            return subprocess.check_output(
                ["sysctl", "-n", "machdep.cpu.brand_string"], text=True
            ).strip()
        except (OSError, subprocess.CalledProcessError):
            return platform.processor() or platform.machine()
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
```

```{code-cell} ipython3
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
```

```{code-cell} ipython3
get_specs()
```

## Test function

Create a test function to test the models:

```{code-cell} ipython3
def test_model(Model, n):

    init_time = list()
    encode_time = list()
    decode_time = list()
    total_time = list()

    # Iterations for computing mean and standard deviation
    iterations = 50

    for i in range(1, iterations + 1):
        # Initialization
        start_process = time.time()
        model = Model(n, 1)
        # Encoding
        start_encode = time.time()
        for dim in range(model.n):
            model.encode(0.5, dim)
        # Decoding
        start_decode = time.time()
        result = model.decode()
        end_process = time.time()

        # Store timings
        init_time.append(start_encode - start_process)
        encode_time.append(start_decode - start_encode)
        decode_time.append(end_process - start_decode)
        total_time.append(end_process - start_process)

    return [
        n,
        np.mean(init_time),
        np.mean(encode_time),
        np.mean(decode_time),
        np.mean(total_time),
        np.std(total_time),
    ]
```

```{code-cell} ipython3
def plot_results(df, title="Model"):
    """Plot all the results"""

    # Total timewith STD
    fig = plt.figure(figsize=(15, 6), dpi=150)

    df.plot(
        x="n",
        y=[4],
        yerr="Total STD",
        uplims=True,
        lolims=True,
        kind="line",
        color="r",
        ax=plt.gca(),
    )
    plt.title(f"{title} - Total time with STD")

    plt.grid(visible=True, which="major", linestyle="-")
    plt.grid(visible=True, which="minor", linestyle="--", alpha=0.2)
    plt.minorticks_on()

    plt.show()

    # Timings insight
    fig = plt.figure(figsize=(15, 6), dpi=150)

    df.plot(x="n", y=[1, 2, 3, 4], kind="line", ax=plt.gca())
    plt.title(f"{title} - Timings insight")

    plt.grid(visible=True, which="major", linestyle="-")
    plt.grid(visible=True, which="minor", linestyle="--", alpha=0.2)
    plt.minorticks_on()

    plt.show()

    # Zooming in
    print("Zooming in:")
    fig = plt.figure(figsize=(15, 6), dpi=150)

    df.plot(x="n", y=[1, 2], kind="line", ax=plt.subplot(1, 2, 1))
    plt.title("Initialization and encoding only")

    plt.grid(visible=True, which="major", linestyle="-")
    plt.grid(visible=True, which="minor", linestyle="--", alpha=0.2)
    plt.minorticks_on()

    ax = plt.subplot(1, 2, 2)
    df[1:19].plot(x="n", y=[1, 2, 3], kind="line", ax=ax)
    df[1:19].plot(x="n", y=[4], yerr="Total STD", kind="line", ax=ax)
    plt.title("Showing results for n < 20")

    plt.grid(visible=True, which="major", linestyle="-")
    plt.grid(visible=True, which="minor", linestyle="--", alpha=0.2)
    plt.minorticks_on()

    plt.show()
```


## AngularModel
We test initialization, encoding, and decoding for an input of .5 on each
dimension. The executable documentation caps the statevector benchmark at
12 qubits so it remains practical on documentation builders.

```{code-cell} ipython3
from qrobot.models import AngularModel

max_n = 12
```

```{code-cell} ipython3
table = list()

for n in range(1, max_n + 1):
    print(f"Testing n={n}", end="\r")
    table.append(test_model(AngularModel, n))
print("             ")

df_angular = pd.DataFrame(
    table, columns=["n", "Initialization", "Encode", "Decode", "Total", "Total STD"]
)
```

Plotting the results:

```{code-cell} ipython3
plot_results(df_angular, "AngularModel")
```

Numerical values:

```{code-cell} ipython3
df_angular
```

___
## LinearModel
We test initialization, encoding, and decoding for an input of .5 on each
dimension up to the same 12-qubit practical documentation limit.

```{code-cell} ipython3
from qrobot.models import LinearModel

max_n = 12
```

```{code-cell} ipython3
table = list()

for n in range(1, max_n + 1):
    print(f"Testing n={n}", end="\r")
    table.append(test_model(LinearModel, n))
print("             ")


df_linear = pd.DataFrame(
    table, columns=["n", "Initialization", "Encode", "Decode", "Total", "Total STD"]
)
```

```{code-cell} ipython3
plot_results(df_linear, "LinearModel")
```

```{code-cell} ipython3
df_linear
```


## Comparison

```{code-cell} ipython3
fig = plt.figure(figsize=(15, 6), dpi=150)

df_angular.plot(x="n", y=[4], kind="line", ax=plt.gca())
df_linear.plot(x="n", y=[4], kind="line", ax=plt.gca())
plt.legend(["AngularModel", "LinearModel"])
plt.title("Total times comparison")

plt.grid(visible=True, which="major", linestyle="-")
plt.grid(visible=True, which="minor", linestyle="--", alpha=0.2)
plt.minorticks_on()

plt.show()
```

```{code-cell} ipython3
fig = plt.figure(figsize=(15, 6), dpi=150)

df_angular.plot(x="n", y=[5], kind="line", ax=plt.gca())
df_linear.plot(x="n", y=[5], kind="line", ax=plt.gca())

plt.legend(["AngularModel", "LinearModel"])
plt.title("Total times STD comparison")

plt.grid(visible=True, which="major", linestyle="-")
plt.grid(visible=True, which="minor", linestyle="--", alpha=0.2)
plt.minorticks_on()

plt.show()
```

```{code-cell} ipython3
fig = plt.figure(figsize=(15, 6), dpi=150)

df_angular[1:19].plot(x="n", y=[4], kind="line", ax=plt.gca())
df_linear[1:19].plot(x="n", y=[4], kind="line", ax=plt.gca())

plt.legend(["AngularModel", "LinearModel"])
plt.title("Total times comparison (n < 20)")

plt.grid(visible=True, which="major", linestyle="-")
plt.grid(visible=True, which="minor", linestyle="--", alpha=0.2)
plt.minorticks_on()

plt.show()
```
