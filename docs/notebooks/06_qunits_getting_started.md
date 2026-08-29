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

# Getting started with qUnits

```{admonition} Research provenance
The Redis-connected qUnit/qBrain architecture is described in [*Quantum-like Modeling
of Cognitive Architectures for Robotics*](https://doi.org/10.5281/zenodo.22068511).
This tutorial demonstrates the current package runtime.
```

```{important}
This tutorial starts qUnit worker processes and therefore requires a Redis
server listening on `localhost:6379`. Install the `qunits` extra and start
Redis before executing this page. Redis is the shared communication and
observable-state sidecar for independently scheduled qUnit processes and the
dashboard.
```

```{code-cell} ipython3
from qrobot.bursts import OneBurst, ZeroBurst
from qrobot.logger import LoggingConfig, configure_logging
from qrobot.models import AngularModel
from qrobot_qunits import QUnit, SensorialUnit, redis_utils
from qrobot_visualization import build_network, draw
from IPython.display import HTML, display
from pathlib import Path
import time
```

```{code-cell} ipython3
# This is application-owned logging. The library does not configure handlers
# unless this opt-in helper is called.
logging_config = LoggingConfig(
    level=10,  # logging.DEBUG
    file_path=Path(".qrobot_logs/qrobot-qunits-debug.log"),
    console=False,  # keep executed-documentation output readable
)
configure_logging(logging_config)
```

## Set up a basic qBrain


First, define a sensorial input:

```{code-cell} ipython3
# Layer 0 - Unit 0
l0_unit0 = SensorialUnit("l0_unit0", sampling_period=0.1, logging_config=logging_config)
```

Then, choose a model and the desired bursts:

```{code-cell} ipython3
print(AngularModel(n=2, tau=10))
print(ZeroBurst())
print(OneBurst())
```

You can use objects like those to create a basic qBrain:

```{code-cell} ipython3
# Layer 1 - Unit 0
l1_unit0 = QUnit(
    name="l1_unit0",
    model=AngularModel(n=1, tau=10),
    burst=OneBurst(),
    sampling_period=0.1,
    in_qunits={0: l0_unit0.id},  # Will receive Input from l0_unit0, dim 0
    logging_config=logging_config,
)

# Layer 1 - Unit 1
l1_unit1 = QUnit(
    name="l1_unit1",
    model=AngularModel(n=1, tau=25),
    burst=ZeroBurst(),
    sampling_period=0.1,
    in_qunits={0: l0_unit0.id},  # Will receive input from l0_unit0, dim 0
    logging_config=logging_config,
)
```

```{image} ./06_imgs/tutorial_qunits_basicnetwork.png
:width: 300px
:align: center
```

```{code-cell} ipython3
l0_unit0
```

```{code-cell} ipython3
l1_unit0
```

```{code-cell} ipython3
l1_unit1
```

Check the default input for `l0_unit0`:

```{code-cell} ipython3
l0_unit0.scalar_reading
```

The input units for each qUnit are:

```{code-cell} ipython3
print(l1_unit0.in_qunits)
print(l1_unit1.in_qunits)
```

Modify `l1_unit1` query:

```{code-cell} ipython3
l1_unit1.query = [0.8]
```

## Real-time processing

Both qUnits sample every 0.1 seconds, but they integrate different numbers of
samples. `l1_unit0` decides every $10\times0.1=1$ second; `l1_unit1` decides
every $25\times0.1=2.5$ seconds.

The important direction of time is:

1. during a window, the qUnit reads and encodes incoming samples;
2. at the right edge, it applies its query to the accumulated state;
3. it performs one binary measurement and publishes the corresponding burst;
4. it resets the model and starts accumulating the next window, while the
   previous burst remains visible.

Therefore, an output drawn just after time $t$ describes the completed window
immediately **before** $t$. It is not a decision about the current sensor sample.

The next cell runs the system in real time, records a snapshot every
`refresh_time`, and changes `l0_unit0.scalar_reading` once per second:

```{code-cell} ipython3
import time
import json
from random import randint
from IPython.display import clear_output

statuses = []
refresh_time = 0.25  # Plot four Redis snapshots per second.
input_change_period = 1.0
run_duration = 30
units = (l0_unit0, l1_unit0, l1_unit1)

for unit in units:
    unit.start()

try:
    for i in range(int(run_duration / refresh_time)):
        time.sleep(refresh_time)
        clear_output(wait=True)

        # Keep each random reading for one second, so both qUnits integrate
        # visible blocks of evidence rather than unrelated high-rate noise.
        if i % int(input_change_period / refresh_time) == 0:
            l0_unit0.scalar_reading = randint(0, 1000) / 1000

        status = redis_utils.redis_status()
        statuses.append(status)
        print(json.dumps(status, indent=1, sort_keys=True))
        print(round((i + 1) * refresh_time, 2), f"/{run_duration} seconds")

    latest_bursts = {
        l1_unit0.name: l1_unit0.get_burst_output(),
        l1_unit1.name: l1_unit1.get_burst_output(),
    }
finally:
    for unit in reversed(units):
        unit.stop()
```

This graph shows the final recorded qBrain network state:

```{code-cell} ipython3
qbrain_graph = build_network(status_dict=statuses[-1])
qbrain_figure = draw(qbrain_graph)
display(HTML(qbrain_figure.to_html(full_html=False, include_plotlyjs=True)))
```

These are the latest outputs that were captured before stopping the units:

```{code-cell} ipython3
latest_bursts
```

`stop()` already removes the keys owned by each unit:

```{code-cell} ipython3
redis_utils.redis_status()
```

To flush the redis to clean all traces (should not be necessary if the qUnits processing loops stopped correctly):

```{code-cell} ipython3
redis_utils.flush_redis()
redis_utils.redis_status()
```

## Visualize the results


The recorded values show how signals evolve over that interval:

```{code-cell} ipython3
:tags: [hide-input]

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

status_df = pd.DataFrame(statuses)
units = [l0_unit0.id + " output", l1_unit0.id + " output", l1_unit1.id + " output"]
status_df = status_df[units]
status_df = status_df.astype(np.float64)
status_df.index = (status_df.index + 1) * refresh_time

sensor_key = l0_unit0.id + " output"
fast_key = l1_unit0.id + " output"
slow_key = l1_unit1.id + " output"


def plot_unit_decisions(unit_specs):
    """Plot sensor evidence followed by one row per qUnit decision stream."""
    fig, axes = plt.subplots(
        1 + len(unit_specs),
        1,
        figsize=(15, 2.7 * (1 + len(unit_specs))),
        sharex=True,
    )
    axes = np.atleast_1d(axes)
    sensor_axis = axes[0]
    sensor_axis.step(status_df.index, status_df[sensor_key], where="post", color="green")
    sensor_axis.set_title("Sensor readings and query targets")

    for decision_axis, (unit, burst_key, burst_label, color) in zip(
        axes[1:], unit_specs, strict=True
    ):
        query = unit.query[0]
        sensor_axis.axhline(query, color=color, ls="--", label=f"{unit.name} query = {query}")
        decision_axis.step(status_df.index, status_df[burst_key], where="post", color=color)
        decision_axis.set_title(burst_label)

        first_decision = status_df[burst_key].dropna().index[0]
        window_duration = unit.model.tau * unit.sampling_period
        decision_times = np.arange(first_decision, run_duration + refresh_time, window_duration)
        decision_axis.vlines(
            decision_times,
            ymin=0,
            ymax=1,
            colors="gray",
            linestyles="dotted",
            linewidth=1,
        )
        # With one qUnit, align its boundaries across evidence and output.
        if len(unit_specs) == 1:
            sensor_axis.vlines(
                decision_times,
                ymin=0,
                ymax=1,
                colors="gray",
                linestyles="dotted",
                linewidth=1,
            )

    sensor_axis.legend(loc="upper right")
    for axis in axes:
        axis.set_ylim(-0.05, 1.05)
        axis.set_ylabel("Value")
    axes[-1].set_xlabel("Elapsed time (s)")
    fig.tight_layout()
    plt.show()


fast_plot = (
    l1_unit0,
    fast_key,
    "Fast qUnit decision (previous 1-second window)",
    "goldenrod",
)
slow_plot = (
    l1_unit1,
    slow_key,
    "Slow qUnit decision (previous 2.5-second window)",
    "blue",
)
```

```{code-cell} ipython3
plot_unit_decisions([fast_plot, slow_plot])
```

The top row contains only evidence and targets: the green trace is the sensor
input, and the dashed lines are the two queries. The middle and bottom rows are
the binary decision streams coming from each qUnit.


Each qUnit turns the previous temporal window of input values into one
query-relative, probabilistic decision.

For the "fast" unit `l1_unit0`:
- due to `OneBurst` it publishes `0` when the measured is state $\lvert 0 \rangle$
- due to the query `0.0`, the $\lvert 0 \rangle$ state is more likely to be measured the closest the input is to `0.0`

For the "swow" unit `l1_unitq`:
- due to `ZeroBurst` it publishes `1` when the measured is state $\lvert 0 \rangle$
- due to the query `0.8`, the $\lvert 0 \rangle$ state is more likely to be measured the closest the input is to `0.8`

Focusing on `l1_unit0`:

```{code-cell} ipython3
print(l1_unit0)
plot_unit_decisions([fast_plot])
```

With query `0.0`, `l1_unit0` tends to emit `0` for windows near `0.0` and `1`
for windows farther from `0.0`. Each output comes from a finite quantum
measurement, so repeated runs can differ even when their inputs match.

Focusing on `l1_unit1`:

```{code-cell} ipython3
print(l1_unit1)
plot_unit_decisions([slow_plot])
```

With query `0.8`, the zero-bit `ZeroBurst` tends to emit `1` for windows near
`0.8` and `0` for more distant windows. Finite measurement makes individual
outputs stochastic rather than a reproducible arithmetic summary such as a mean.

## Logging and debugging qUnits

Logging is opt-in. Configure a rotating-free debug file and the console in the
application that creates qUnits:

```{code-cell} ipython3
# The same config is passed to each unit above. This is important on platforms
# using `spawn`, where workers do not inherit the parent process's handlers.
logging_config
```

The resulting log can be inspected without relying on a library-managed file:

```{code-cell} ipython3
print("\n".join(logging_config.file_path.read_text().splitlines()[-20:]))
```

```{code-cell} ipython3
print(
    "Time window time:",
    l1_unit1.sampling_period * l1_unit1.model.tau,
    "seconds",
)
matching_lines = [
    line
    for line in logging_config.file_path.read_text().splitlines()
    if "l1_unit1" in line and "Output state =" in line
]
print("\n".join(matching_lines[-10:]))
```
