# Simulator API

```{warning}
`qrobot_simulator` is experimental and its interfaces may change between minor releases.
```

`qrobot_simulator` provides two small closed-loop worlds for studying how sensor
histories become robot actions. Each world separates four concerns:

1. the world advances physical state and computes normalized sensor readings;
2. a robot passes those readings to its brain;
3. the brain returns normalized actuator values;
4. an optional live view renders state without participating in the simulation.

This common boundary allows each world to run a classical or quantum robot. Headless
methods use the same world dynamics without constructing Matplotlib figures. Quantum
robots additionally require a running Redis server for communication among
independently scheduled qUnits. Each simulator also has a separate `analysis` package
for controlled inputs and recorded measurements; these tools observe the simulation
without becoming part of the world or robot behavior.

Install the simulator dependencies and start either interactive example with:

```console
poetry install -E simulator
poetry run python examples/grasping_world.py --gripper quantum
poetry run python examples/bug_world.py --controller quantum
```

The [grasping-world notebook](../notebooks/07_object_grasping_world.md) explains
the sensors, robot brains, and fixed comparison. The
[bug-world notebook](../notebooks/08_bug_like_robot.md) explains the predator/prey
interaction and the perceptual and cognitive layers.

## Grasping world

The grasping world contains a stationary gripper and a blue ball moving along its
sensor axis. `ReactiveGripper` uses only the latest readings. `ClassicalGripper`
averages fixed temporal windows, while `QuantumGripper` processes equal-duration
histories through its qBrain. All three use the same world interface:

```python
from qrobot_simulator.grasping_world import ClassicalGripper, GraspingWorld

world = GraspingWorld.demo(ClassicalGripper(), seed=7)
world.run_robot_headless(duration=20.0, dt=0.05)

print(world.correct_grips, world.missed_grips, world.empty_grips)
```

`GraspingWorld.demo()` keeps the ball's random movement for interactive use. The
[grasping analysis API](grasping_analysis.md) provides predefined ball visits and
raw recording when the same situation must be measured across different brains.

`GraspingWorldLiveView` can display the same world or save a frame; it is unnecessary for headless runs.

```{eval-rst}
.. autoclass:: qrobot_simulator.grasping_world.GraspingWorld
   :members: demo, step, run_headless, run_robot_headless, sensor_readings

.. autoclass:: qrobot_simulator.grasping_world.ClassicalGripper

.. autoclass:: qrobot_simulator.grasping_world.ReactiveGripper

.. autoclass:: qrobot_simulator.grasping_world.QuantumGripper

.. autoclass:: qrobot_simulator.grasping_world.GraspingWorldLiveView
   :members: update, save, close

```

## Bug world

The bug world contains one controlled brown bug, blue prey, and a red predator.
`ClassicalBug` maps stereo RGB and proximity readings directly to five actions.
`QuantumBug` can include intermediate prey and threat qUnits before producing the
same actions. `BugWorld` records contacts, boundary crossings, and complete
time-series data:

```python
from qrobot_simulator.bug_world import BugWorld, ClassicalBug

world = BugWorld.demo(ClassicalBug(), seed=7)
record = world.run_recorded_headless(duration=20.0, dt=0.05)

print(world.bitten_prey, world.predator_bites)
```

`BugWorldLiveView` displays the world state and current brain diagnostics without changing the simulation.

```{eval-rst}
.. autoclass:: qrobot_simulator.bug_world.BugWorld
   :members: demo, step, run_headless, run_robot_headless, run_recorded_headless, snapshot, sensor_readings

.. autoclass:: qrobot_simulator.bug_world.ClassicalBug

.. autoclass:: qrobot_simulator.bug_world.QuantumBug

.. autoclass:: qrobot_simulator.bug_world.BugWorldLiveView
   :members: update, save, close
```
