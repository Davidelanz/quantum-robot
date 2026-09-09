# Grasping analysis API

The interactive grasping demo uses a randomly wandering ball. The analysis package
supports measured comparisons by presenting the same predefined ball visit to each
robot. These tools are separate from `GraspingWorld`: they configure and observe the
demonstrated behavior without changing a robot's decisions.

A `GraspingEncounter` defines the ball's starting distance and movement. Negative
velocity approaches the jaws and positive velocity moves away. Its opportunity
interval states when capture counts as a valid response; the robots cannot read this
interval. Optional noise, dropouts, and false detections alter only the proximity
reading.

```python
from qrobot_simulator.grasping_world import ClassicalGripper
from qrobot_simulator.grasping_world.analysis import (
    ControlledGraspingWorld,
    GraspingEncounter,
    MotionSegment,
    ProximityDisturbance,
    TimeInterval,
    record_encounter,
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

world = ControlledGraspingWorld.create(ClassicalGripper(), encounter, seed=7)
record = record_encounter(world, duration=encounter.duration, dt=0.05)
print(record.outcome.label, record.outcome.capture_latency)
```

`record.samples` contains the readings, jaw command, and physical state at each
step. `record.events` identifies closing, capture, consumption, opening, and failed
actions. `record.outcome` derives the encounter result and response times from those
events. `record.metadata` retains the configurations, seeds, duration, and physics
step needed to identify the run. Trial generation, parameter selection, aggregate
statistics, and paper figures belong in the experiment repository.

```{eval-rst}
.. autoclass:: qrobot_simulator.grasping_world.analysis.ControlledGraspingWorld
   :members: create

.. autoclass:: qrobot_simulator.grasping_world.analysis.GraspingEncounter
   :members: duration, velocity_at, is_valid_opportunity

.. autoclass:: qrobot_simulator.grasping_world.analysis.MotionSegment

.. autoclass:: qrobot_simulator.grasping_world.analysis.TimeInterval

.. autoclass:: qrobot_simulator.grasping_world.analysis.ProximityDisturbance

.. autoclass:: qrobot_simulator.grasping_world.analysis.GraspingRunRecord

.. autoclass:: qrobot_simulator.grasping_world.analysis.GraspingSample

.. autoclass:: qrobot_simulator.grasping_world.analysis.GraspingEvent

.. autoclass:: qrobot_simulator.grasping_world.analysis.GraspingOutcome

.. autoclass:: qrobot_simulator.grasping_world.analysis.GraspingRunMetadata
```
