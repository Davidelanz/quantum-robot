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

```{important}
This tutorial starts qUnit worker processes and therefore requires a Redis
server listening on `localhost:6379`. Install the `qunits` extra and start
Redis before building this page.
```

```{code-cell} ipython3
from qrobot.bursts import OneBurst, ZeroBurst
from qrobot.logger import LoggingConfig, configure_logging
from qrobot.models import AngularModel
from qrobot_qunits import QUnit, SensorialUnit, redis_utils
from qrobot_visualization import draw, graph
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

+++

First, define a sensorial input:

```{code-cell} ipython3
# Layer 0 - Unit 0
l0_unit0 = SensorialUnit("l0_unit_0", Ts=0.1, logging_config=logging_config)
```

```{code-cell} ipython3
l0_unit0
```

Then, define a model and the desired bursts:

```{code-cell} ipython3
AngularModel(n=2, tau=10)
```

```{code-cell} ipython3
ZeroBurst()
```

```{code-cell} ipython3
OneBurst()
```

You can use objects like those to create a basic qBrain:

```{image} ./06_imgs/tutorial_qunits_basicnetwork.png
:width: 300px
:align: center
```

```{code-cell} ipython3
# Layer 1 - Unit 0
l1_unit0 = QUnit(
    name="l1_unit0",
    model=AngularModel(n=1, tau=10),
    burst=OneBurst(),
    Ts=0.3,
    in_qunits={0: l0_unit0.id},  # Will receive Input from l0_unit0, dim 0
    logging_config=logging_config,
)

# Layer 1 - Unit 1
l1_unit1 = QUnit(
    name="l1_unit1",
    model=AngularModel(n=1, tau=25),
    burst=ZeroBurst(),
    Ts=0.2,
    in_qunits={0: l0_unit0.id},  # Will receive input from l0_unit0, dim 1
    logging_config=logging_config,
)
```

```{code-cell} ipython3
l1_unit0
```

```{code-cell} ipython3
l1_unit1
```

## Inputs and queries

+++

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
l1_unit1.query = 0.8
```

## Real-time processing

```{code-cell} ipython3
l0_unit0.start()
l1_unit0.start()
l1_unit1.start()
```

Visualize the time evolution of the system from the redis status for 30 seconds changing the input with a random input:

```{code-cell} ipython3
import time
import json
from random import randint
from IPython.display import clear_output

statuses = []
refresh_time = 0.5  # Read statuses every 0.5 seconds

for i in range(int(30 * (1 / refresh_time))):
    # Wait and then clean the output
    time.sleep(refresh_time)
    clear_output(wait=True)

    # Change input every 2 second
    if (i * refresh_time) % 2 == 0:
        l0_unit0.scalar_reading = randint(0, 1000) / 1000

    # Read statused and store it
    status = redis_utils.redis_status()
    statuses.append(status)

    # Print output
    print(json.dumps(status, indent=1, sort_keys=True))
    print(int(i * refresh_time), "/30 seconds")

    # Plot graph
    qbrain_graph = graph(status)
    draw(qbrain_graph, show=False)
```

Read manually the latest outputs of the qunits found on the redis database:

```{code-cell} ipython3
l1_unit0.get_burst_output()
```

```{code-cell} ipython3
l1_unit1.get_burst_output()
```

Stop the processing loops:

```{code-cell} ipython3
l0_unit0.stop()
l1_unit0.stop()
l1_unit1.stop()
```

Flush the redis to clean all traces (should not be necessary if the qUnits processing loops stopped correctly):

```{code-cell} ipython3
redis_utils.redis_status()
```

```{code-cell} ipython3
redis_utils.flush_redis()
```

## Visualize the results

+++

We can visualize the time evolution of such time period:

```{code-cell} ipython3
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

status_df = pd.DataFrame(statuses)
units = [l0_unit0.id + " output", l1_unit0.id + " output", l1_unit1.id + " output"]
status_df = status_df[units]
status_df = status_df.astype(np.float64)
status_df.index = status_df.index * refresh_time

fig, ax = plt.subplots(1, 1, figsize=(15, 5))
# Plot time evolution
styles = ["g", "y", "b"]
status_df[units].plot(style=styles, ax=ax)
# Plot queries as dashed lines
ax.hlines(
    y=l1_unit0.query, xmin=0, xmax=30, linewidth=1, color="y", linestyles="dashed"
)
ax.hlines(
    y=l1_unit1.query, xmin=0, xmax=30, linewidth=1, color="b", linestyles="dashed"
)
plt.show()
```

Focusing on `l1_unit0`:

```{code-cell} ipython3
print(l1_unit0)
fig, ax = plt.subplots(1, 1, figsize=(15, 5))
# Plot time evolution
units = [l0_unit0.id + " output", l1_unit0.id + " output"]
styles = ["g", "b"]
status_df[units].plot(style=styles, ax=ax)
# Plot time windows
t_start = status_df[l1_unit0.id + " output"].dropna().index[0]
t_step = l1_unit0.model.tau * l1_unit0.Ts
t_windows = np.arange(t_start, 31, t_step)
plt.vlines(x=t_windows, ymin=0, ymax=1, colors="gray", ls="dotted", lw=1)
# Plot query as dashed line
ax.hlines(y=l1_unit0.query, xmin=t_start, xmax=30, linewidth=1, color="b", ls="dashed")
plt.show()
```

Focusing on `l1_unit1`:

```{code-cell} ipython3
print(l1_unit1)
fig, ax = plt.subplots(1, 1, figsize=(15, 5))
# Plot time evolution
units = [l0_unit0.id + " output", l1_unit1.id + " output"]
styles = ["g", "b"]
status_df[units].plot(style=styles, ax=ax)
# Plot time windows
t_start = status_df[l1_unit1.id + " output"].dropna().index[0]
t_step = l1_unit1.model.tau * l1_unit1.Ts
t_windows = np.arange(t_start, 31, t_step)
plt.vlines(x=t_windows, ymin=0, ymax=1, colors="gray", ls="dotted", lw=1)
# Plot query as dashed line
ax.hlines(y=l1_unit1.query, xmin=t_start, xmax=30, linewidth=1, color="b", ls="dashed")
plt.show()
```

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
print("Time window time:", l1_unit1.Ts * l1_unit1.model.tau, "seconds")
matching_lines = [
    line
    for line in logging_config.file_path.read_text().splitlines()
    if "l1_unit1" in line and "Output state =" in line
]
print("\n".join(matching_lines[-10:]))
```
