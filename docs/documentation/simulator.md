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

This common boundary allows each world to run either a classical robot or a quantum
robot. Headless methods use the same world dynamics without constructing Matplotlib
figures. Quantum robots additionally require a running Redis server for communication
among independently scheduled qUnits.

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

The grasping world has two separate ways to start:

- `GraspingWorld.demo(...)` creates the visual demonstration. Its ball continues
  to wander randomly, changing speed and direction as the simulation runs.
- `GraspingWorld.controlled(...)` creates one predefined visit of the ball. This
  mode is intended for comparing the classical and quantum grippers fairly.

That predefined visit is called a `GraspingEncounter`. It says where the ball
starts, how long it moves at each velocity, and when it is close enough for a
grasp to count as a valid response. Negative velocity moves the ball toward the
jaws and positive velocity moves it away. The opportunity interval is only a
label for later scoring: the robots cannot see it, and it does not change the
physics. The encounter can also add sensor noise, dropouts, or false detections:

```python
from qrobot_simulator.grasping_world import (
    GraspingEncounter,
    MotionSegment,
    ProximityDisturbance,
    TimeInterval,
)

encounter = GraspingEncounter(
    initial_distance=24.0,
    motion=(
        MotionSegment(duration=2.0, velocity=-5.0),
        MotionSegment(duration=2.5, velocity=0.0),
        MotionSegment(duration=2.0, velocity=5.0),
    ),
    opportunity=TimeInterval(start=1.8, duration=2.7),
    disturbance=ProximityDisturbance(noise_standard_deviation=0.05),
)

world = GraspingWorld.controlled(ClassicalGripper(), encounter, seed=7)
world.run_robot_headless(duration=encounter.duration, dt=0.05)
```

An experiment creates three fresh worlds from the same encounter and seed: one for
each gripper. Every robot therefore sees the same ball visit and sensor disturbance.
Differences in their responses can then be attributed to their brains rather than
to one receiving an easier random trajectory. Noise is derived from the seed and
simulated time, so rendering or reading a sensor for diagnostics does not change a
later value.

`GraspingWorldLiveView` can display the same world or save a frame; it is unnecessary for headless runs.

```{eval-rst}
.. autoclass:: qrobot_simulator.grasping_world.GraspingWorld
   :members: demo, controlled, step, run_headless, run_robot_headless, sensor_readings

.. autoclass:: qrobot_simulator.grasping_world.ClassicalGripper

.. autoclass:: qrobot_simulator.grasping_world.ReactiveGripper

.. autoclass:: qrobot_simulator.grasping_world.QuantumGripper

.. autoclass:: qrobot_simulator.grasping_world.GraspingWorldLiveView
   :members: update, save, close

.. autoclass:: qrobot_simulator.grasping_world.GraspingEncounter
   :members: duration, velocity_at, is_valid_opportunity

.. autoclass:: qrobot_simulator.grasping_world.MotionSegment

.. autoclass:: qrobot_simulator.grasping_world.TimeInterval

.. autoclass:: qrobot_simulator.grasping_world.ProximityDisturbance
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
