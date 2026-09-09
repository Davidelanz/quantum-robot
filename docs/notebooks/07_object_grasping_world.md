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

# Grasping world

```{warning}
`qrobot_simulator` is experimental and its interfaces may change between minor releases.
```

A stationary gripper combines proximity with contact feedback while a ball moves
stochastically along its sensor axis. The same world accepts a `ReactiveGripper`,
`ClassicalGripper`, or `QuantumGripper`.

```{image} ./07_imgs/grasping_live_world.png
:alt: Two-dimensional grasping world with sensor regions and qBrain signals
:width: 680px
:align: center
```

The simulation isolates a single perception-to-action problem. A blue ball moves
toward and away from the stationary gripper. The gripper must close while the ball
is between its jaws, use the internal touch sensor to recognize a successful catch,
and reopen in time for the next approach. The world records catches, missed visits,
empty closures, and response times. It supplies all three grippers with the same sensor
interface and applies their commands to the same physical interaction.

## Setup

The experiment contains three components: a stationary gripper, a ball moving
along the gripper's sensor axis, and an arena that computes sensing and contact.
The orange region in the figure is the complete distance-sensor range. Its inner
green portion is the space enclosed by the jaws. The touch pads lie inside the
jaws, so they report contact only after a closure reaches the ball.

The sensor limits below define the distance normalization, while the grippable
distance marks how far the jaws can reach. The prey consumption time is how long
a successful catch must remain between the closed jaws before the prey disappears.
Ball speed determines how quickly this geometry changes.

```{code-cell} ipython3
import pandas as pd

from qrobot_simulator.grasping_world.robots.config import (
    BALL_PREY_CONFIG,
    CLASSICAL_GRIPPER_CONFIG,
    QUANTUM_GRIPPER_CONFIG,
    REACTIVE_GRIPPER_CONFIG,
)
from qrobot_simulator.grasping_world.world.config import WORLD_CONFIG

setup = {
    "sensor near / far (cm)": f"{WORLD_CONFIG.near_distance:g} / {WORLD_CONFIG.far_distance:g}",
    "grippable distance (cm)": WORLD_CONFIG.grippable_distance,
    "prey consumption time (s)": WORLD_CONFIG.consumption_time,
    "ball maximum speed (cm/s)": BALL_PREY_CONFIG.max_speed,
}
pd.DataFrame.from_dict(setup, orient="index", columns=["value"])
```

The left plot shows how physical distance becomes a qUnit input. Objects inside the
near limit produce `1`, objects beyond the far limit produce `0`, and intermediate
distances are interpolated. This direction matches the proximity query: a larger
input means a closer object. The right plot shows the two touch states. An empty
gripper produces `1`; contact with a ball produces `0`.

```{code-cell} ipython3
import matplotlib.pyplot as plt
import numpy as np
from qrobot_simulator.grasping_world.utils.sensors import proximity_reading, touch_reading

distances = np.linspace(0, BALL_PREY_CONFIG.max_distance, 200)
values = [
    proximity_reading(d, near=WORLD_CONFIG.near_distance, far=WORLD_CONFIG.far_distance)
    for d in distances
]
fig, (distance_axis, touch_axis) = plt.subplots(1, 2, figsize=(9, 3))
distance_axis.plot(distances, values)
distance_axis.set(xlabel="Distance (cm)", ylabel="Proximity", ylim=(-0.05, 1.05))
touch_axis.bar(["empty", "contact"], [touch_reading(False), touch_reading(True)])
touch_axis.set(ylabel="Touch input", ylim=(0, 1.05))
fig.tight_layout()
plt.show()
```

## Reactive gripper

All grippers see only normalized proximity and touch; none reads the ball's
position directly. They return one normalized command, where values above the
gripper threshold close the jaws.

`ReactiveGripperBrain` is the no-memory reference. It closes as soon as the current
proximity reading crosses its threshold. While closed, current touch contact keeps
the jaws closed; an empty touch reading opens them. A single brief or corrupted
sample can therefore cause it to react.

```{code-cell} ipython3
pd.DataFrame.from_dict(
    {
        "proximity threshold": REACTIVE_GRIPPER_CONFIG.proximity_threshold,
        "touch-contact threshold": REACTIVE_GRIPPER_CONFIG.contact_threshold,
        "jaw activation threshold": REACTIVE_GRIPPER_CONFIG.gripper_threshold,
    },
    orient="index",
    columns=["value"],
)
```

## Classical gripper

`ClassicalGripperBrain` is the deterministic temporal comparison. It divides each
sensor stream into fixed, non-overlapping windows and computes the arithmetic mean
of every completed window. The proximity and empty-gripper means then enter the
same strict mean threshold used by the quantum actuator. Its sampling period and
window lengths equal those of the two qUnits, separating temporal memory from the
AngularModel and its stochastic measurement.

Its timing and decision thresholds are printed from `ClassicalGripperConfig`:

```{code-cell} ipython3
pd.DataFrame.from_dict(
    {
        "sampling period (s)": CLASSICAL_GRIPPER_CONFIG.sampling_period,
        "proximity window (s)": CLASSICAL_GRIPPER_CONFIG.sampling_period
        * CLASSICAL_GRIPPER_CONFIG.proximity_tau,
        "empty-gripper window (s)": CLASSICAL_GRIPPER_CONFIG.sampling_period
        * CLASSICAL_GRIPPER_CONFIG.empty_gripper_tau,
        "jaw activation threshold": CLASSICAL_GRIPPER_CONFIG.gripper_threshold,
    },
    orient="index",
    columns=["value"],
)
```

The source below is the actual brain class imported from the package:

```{code-cell} ipython3
from inspect import getsource
from IPython.display import Code
from qrobot_simulator.grasping_world.robots.classical_gripper import ClassicalGripperBrain

Code(getsource(ClassicalGripperBrain), language="python")
```

## Quantum gripper

`QuantumGripperBrain` queries a short proximity history qUnit and a longer empty-gripper
history qUnit. Both measured bursts feed one actuator, which closes when their mean
exceeds its threshold. The shorter proximity window lets the robot respond to an
approaching ball sooner than the longer touch window responds to contact.

Its sampling, temporal windows, queries, and actuator threshold are taken from
`QuantumGripperConfig`:

```{code-cell} ipython3
pd.DataFrame.from_dict(
    {
        "sampling period (s)": QUANTUM_GRIPPER_CONFIG.sampling_period,
        "proximity window (s)": QUANTUM_GRIPPER_CONFIG.sampling_period
        * QUANTUM_GRIPPER_CONFIG.proximity_tau,
        "proximity query": QUANTUM_GRIPPER_CONFIG.proximity_query,
        "empty-gripper window (s)": QUANTUM_GRIPPER_CONFIG.sampling_period
        * QUANTUM_GRIPPER_CONFIG.empty_gripper_tau,
        "empty-gripper query": QUANTUM_GRIPPER_CONFIG.empty_gripper_query,
        "jaw activation threshold": QUANTUM_GRIPPER_CONFIG.gripper_threshold,
    },
    orient="index",
    columns=["value"],
)
```

```{code-cell} ipython3
from IPython.display import HTML
from qrobot_qunits import RedisConfig
from qrobot_simulator.grasping_world.robots.quantum_gripper import QuantumGripperBrain
from qrobot_visualization import build_network, draw

quantum_brain = QuantumGripperBrain(RedisConfig())
architecture = draw(build_network(quantum_brain.units))
HTML(architecture.to_html(include_plotlyjs="cdn", full_html=False, config={"responsive": True}))
```

Blue nodes form the sensor and perceptual path; the green node is the actuator.
The arrows identify which outputs become inputs to the next unit. The graph itself
reports the configured models, queries, periods, and wiring. The proximity burst
rises when recent readings resemble a nearby ball. The empty-gripper burst falls
as contact readings accumulate. Their combination supplies the jaw command.

## Simulated interaction

The ball receives random changes in velocity, creating approaches, reversals, and
near misses rather than a scripted passage. A residence limit prevents it from
remaining indefinitely under the gripper. Arena boundaries and closed jaws constrain
its motion.

When the jaws close around the ball, the ball is held and the touch input changes.
The **prey consumption time** is the simulated chewing interval for which a caught
ball remains between the closed jaws. At its end the consumed ball disappears, making
the touch sensor report an empty gripper. The brain must then open the jaws; only that
opening makes a new ball appear farther away. Opening before consumption releases the
same ball and lets it escape. Closing without
the ball counts as an **empty grip**. A visit ending inside the jaws counts as a
**correct grip**, while an uncaught visit counts as a **missed grip**. Response time
is measured from entry into the grippable region until capture. The renderer shows
this world state and the current brain signals without affecting either one.

## Run the example

With Redis listening on `localhost:6379`:

```bash
python examples/grasping_world.py --gripper quantum
```

Use `--gripper reactive`, `--gripper classical`, or `--gripper quantum` to select
the brain. A fixed `--seed` repeats the random ball motion, while `--speed`
accelerates the scheduled qBrain up to the limit reported by `--help`. A bounded
headless run can save its final frame:

```bash
python examples/grasping_world.py --gripper quantum --duration 10 --seed 7 --no-show \
  --save-world grasping_live_world.png
```

## Fixed headless comparison

Ten paired trials expose the classical and quantum grippers to the same initial
conditions and random motion. This is a descriptive implementation check rather
than a parameter search or a claim of statistical superiority. The cell prints the
experimental setup.

```{code-cell} ipython3
:tags: [hide-input]

from random import Random
from statistics import mean
from qrobot_simulator.grasping_world import ClassicalGripper, GraspingWorld, QuantumGripper

N_TRIALS = 5
TRIAL_SEEDS = tuple(Random(2026).sample(range(1, 100_000), N_TRIALS))
TRIAL_DURATION = 60.0
PHYSICS_STEP = 0.05
QUANTUM_SPEED = 10.0

display(
    pd.DataFrame.from_dict(
        {
            "paired trials": len(TRIAL_SEEDS),
            "duration (simulated s)": TRIAL_DURATION,
            "physics step (s)": PHYSICS_STEP,
            "quantum time ratio": QUANTUM_SPEED,
        },
        orient="index",
        columns=["value"],
    )
)


def summarize_trial(controller: str, world: GraspingWorld) -> dict[str, float | int | str]:
    """Collect the outcome measures of one run."""
    visits = world.correct_grips + world.missed_grips
    return {
        "controller": controller,
        "correct": world.correct_grips,
        "missed": world.missed_grips,
        "empty": world.empty_grips,
        "capture_rate": world.correct_grips / visits if visits else float("nan"),
        "mean_response_s": mean(world.grip_response_times)
        if world.grip_response_times
        else float("nan"),
    }


def run_trial(controller: str, seed: int) -> dict[str, float | int | str]:
    """Run either brain through the shared headless interface."""
    gripper = (
        ClassicalGripper()
        if controller == "classical"
        else QuantumGripper(RedisConfig(), speed=QUANTUM_SPEED)
    )
    world = GraspingWorld.demo(gripper, seed=seed)
    world.run_robot_headless(TRIAL_DURATION, PHYSICS_STEP)
    return summarize_trial(controller, world)


trial_results = pd.DataFrame(
    [
        {"seed": seed, **run_trial(controller, seed)}
        for seed in TRIAL_SEEDS
        for controller in ("classical", "quantum")
    ]
)
```

Capture rate is the fraction of completed visits ending in a catch. Response time
runs from entry into the grippable region to capture. The median describes a typical
trial and the sample standard deviation shows variation among trajectories.

```{code-cell} ipython3
trial_results.groupby("controller", sort=False)[
    ["correct", "missed", "empty", "capture_rate", "mean_response_s"]
].agg(["median", "std"]).round(3)
```
