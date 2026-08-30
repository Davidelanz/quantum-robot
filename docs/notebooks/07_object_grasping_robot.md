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

# Grasping robot: a live object-grasping qBrain

```{warning}
`qrobot_simulator` is experimental. This tutorial uses scenario-specific
grasping, sensing, movement, and rendering interfaces that may change between
minor releases.
```

```{admonition} Research provenance
This tutorial implements the object-grasping
architecture in [*Quantum-like Modeling of Cognitive Architectures for
Robotics*](https://doi.org/10.5281/zenodo.22068511). The architecture diagram
is reproduced by the executable graph below; the robot photographs are
archival assets of this master's thesis work.
The two-dimensional world is rendered by
`examples/grasping_robot.py` using the current Redis-connected qUnit implementation.
```

In [*Quantum-like Modeling of Cognitive Architectures for
Robotics*](https://doi.org/10.5281/zenodo.22068511) we use a carnivorous-plant
metaphor: a stationary robot waits for an
object, closes its gripper when the object is reachable, and uses an internal
touch sensor to detect contact. The stationary design focuses the example on
the signal path from distance and touch readings to gripper actuation.

| Open gripper | Closed gripper |
| :---: | :---: |
| ![LEGO Mindstorms NXT grasping robot with its gripper open](./07_imgs/grasping_robot.jpg) | ![LEGO Mindstorms NXT grasping robot with its gripper closed](./07_imgs/grasping_robot_closed.jpg) |

## Architecture

```{code-cell} ipython3
from IPython.display import HTML
from qrobot_qunits import RedisConfig
from qrobot_simulator.grasping_robot import build_grasping_qbrain
from qrobot_visualization import build_network, draw

sensors, qunits, actuator = build_grasping_qbrain(redis_config=RedisConfig())
architecture = draw(build_network((sensors, qunits, actuator)))
HTML(
    architecture.to_html(
        include_plotlyjs="cdn",
        full_html=False,
        config={"responsive": True},
        default_width="100%",
    )
)
```

Read the graph from left to right. Blue nodes are sensor interfaces or
perceptual qUnits, and the green node is the actuator. The arrows show the
direction in which each unit consumes the previous unit's output. The graph is
interactive, so it can be zoomed and panned when inspecting labels or wiring.

The signal path has three stages:

1. **Sensors.** `grasp_distance` normalizes ultrasonic distance to $[0,1]$;
   `1` means closest and `0` means farthest or out of range. `grasp_touch`
   produces `1` while the gripper is empty and `0` while its internal switch
   is pressed.
2. **Perception.** `grasp_proximity` compares a one-second distance history
   with query `[1.0]`. `grasp_empty` compares a five-second touch history with
   the same query. Both publish a stochastic binary `ZeroBurst` after a
   complete temporal window.
3. **Actuation.** `grasp_gripper` averages the two bursts and closes only when
   their mean is strictly greater than its `0.5` threshold.

The **touch sensor is inside the gripper**. It reports contact only after the
jaws have closed around prey. In the carnivorous-plant analogy, that contact is
also the plant's feedback that it is still consuming what it caught. Once the
prey has been absorbed, the contact disappears: “I have absorbed what I could;
now I can open for the next one.” Thus touch is not an external presence
detector. While the robot waits with open jaws it merely reports that the
gripper is empty, so proximity is still needed to initiate a grasp.

The two sensors answer different questions:

- proximity asks, “is there an object close enough to attempt a grasp?”;
- touch asks, “is the gripper still empty, or did that attempt make contact?”

For binary qUnit bursts, the actuator's strict `> 0.5` threshold acts like an
AND gate:

| Proximity burst | Empty-gripper burst | Mean | Command |
| ---: | ---: | ---: | --- |
| 0 | 1 | 0.5 | remain open: nothing is reachable |
| 1 | 1 | 1.0 | close: an object is near and the gripper is empty |
| 1 | 0 | 0.5 | open after contact has persisted through the slow window |

The unequal windows are the point of the architecture. Proximity supplies a
relatively fast assessment of the approaching object, whereas touch supplies
slower feedback about the result of the grasp. Each decision represents a
whole sensor history, rather than forwarding the latest raw sample directly to
the motor.

The example studies one specific question from the thesis: how independently
timed, stochastic quantum-like decisions can represent perceptual evidence and
feedback before an actuator combines them. Its world contains one object type,
deterministic sensor interfaces, and a single gripper behavior. Those boundaries
define the experiment implemented below.


## Sensor interfaces

The simulated ultrasonic sensor first produces a continuous distance in
centimetres. `proximity_interface` then converts it to the normalized scalar
that a `SensorialUnit` accepts. The mapping follows the architecture diagram:
distances at or below 5 cm map to `1`, distances at or above 20 cm map to `0`,
and values between those limits are linearly interpolated. These values come
from the robot's geometry: 5 cm is the distance from the ultrasonic sensor to
the robot's front surface, while 15 cm is the outer entrance to the grippable
area. The remaining 15--20 cm interval provides advance warning before an
object reaches the jaws. Thus *closer means a higher input*. This inversion of
physical distance is intentional: with query `[1.0]`, $p_1$ asks whether its
temporal window resembles the closest-object target. No extra negation or
complementary query is required.

The touch interface is already binary: `False` (empty/not pressed) maps to `1`,
and `True` (pressed) maps to `0`.

```{code-cell} ipython3
import matplotlib.pyplot as plt
import numpy as np
from qrobot_simulator.grasping_robot import proximity_interface, touch_interface

distances = np.linspace(0, 45, 200)
proximity_values = [proximity_interface(distance) for distance in distances]

fig, (distance_axis, touch_axis) = plt.subplots(1, 2, figsize=(10, 3.2))
distance_axis.plot(distances, proximity_values)
distance_axis.set(
    xlabel="Object distance (cm)",
    ylabel="Normalized proximity",
    ylim=(-0.05, 1.05),
    title="Distance interface",
)
touch_axis.bar(["empty", "pressed"], [touch_interface(False), touch_interface(True)])
touch_axis.set(ylabel="Normalized signal", ylim=(0, 1.05), title="Touch interface")
fig.tight_layout()
plt.show()
```

## Live demo

The `BallPrey` robot starts gently at a varied middle-to-far position and then wanders by
receiving random changes in speed and direction. Those changes do not inspect
its position: there is no rule steering it toward or away from the mouth. Only
collisions with the arena edges or closed jaws depend on location. This makes
hesitation, reversals, near misses, and deceptive approaches possible
throughout the sensor range instead of producing a scripted beeline followed
by back-and-forth motion. Pass `--seed` to replay the same random motion.

```{image} ./07_imgs/grasping_live_world.png
:alt: Live 2-D grasping world with robot, ball, sensor regions, and qBrain signals
:width: 680px
:align: center
```

The orange band represents the complete 20 cm distance-sensor range, measured
from the sensor origin beside the robot body to the dotted orange boundary.
The green 5--15 cm section is the physical grippable area; 5 cm ends at the
robot surface, 15 cm is the jaws' outer entrance, and 15--20 cm is the warning
region. The dashed line measures to the ball centre, matching the value shown
in cm.
The two small grey pads at the inner tips of the jaws are the physical touch sensor.
When closed jaws contact the ball, the touch signal changes from empty (`1`) to pressed (`0`).

Closed jaws are also a physical barrier. A ball caught while the jaws close is
held while the plant “digests” it, and an outside ball cannot pass through
closed jaws. After 2.5 simulated seconds the caught ball vanishes and a new
ball appears at a random far position, ready for another encounter.
The live score counts a **correct** grip on closure around a ball, a **missed**
grip when a visit to the jaw area ends uncaught, and an **empty** grip whenever
the jaws close without a ball inside.

The faster proximity unit responds first.
The gripper closes only once both bursts are active.
The contact with the ball then changes the touch interface immediately,
but the slow qUnit needs a complete temporal window before its burst changes.
This delay is the architectural effect the simulation exposes visually:
actuation is based on temporally integrated qUnit decisions rather than raw sensor values.

The result is stochastic because each qUnit produces a one-shot measurement at the end of its window.
Exact transition times can vary between runs, while the wiring and temporal scales remain fixed.

## Run the example

With Redis listening on `localhost:6379`:

```bash
python examples/grasping_robot.py
```

The encounter repeats until its window is closed or `Ctrl-C` is pressed.
`--speed` selects a simulation-time/wall-clock-time ratio in `(0, 10]` while
preserving the ratio between the one- and five-second qUnit windows. Both
qUnits are warmed up before the scenario clock starts, so process startup is
not mistaken for sensor history. `--seed` makes the random path reproducible.
A reproducible headless frame can also be saved:

```bash
python examples/grasping_robot.py --duration 10 --seed 7 --no-show \
  --save-world grasping_live_world.png
```

The thin runner creates only its own Redis keys and removes them when its
workers stop. It requires neither ROS nor LEGO hardware; the packaged
`GraspingRobot` and `BallPrey` define the participants, `GraspingWorld` owns
their physical interaction and sensor readings, and `GraspingWorldLiveView`
renders that state.

## Reference

- D. Lanza, [*Quantum-like Modeling of Cognitive Architectures for
  Robotics*](https://doi.org/10.5281/zenodo.22068511), Zenodo, 2020.
