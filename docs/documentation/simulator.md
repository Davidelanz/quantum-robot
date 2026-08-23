# Embodied simulators

The simulator extension contains two examples: the stationary
`grasping_robot` and the mobile `bug_world`.
Both separate physical world state, a self-contained Redis-connected robot,
and persistent Matplotlib presentation.

The examples require the `simulator` extra and a Redis server on
`localhost:6379`. Run them from a repository checkout with Poetry:

```console
poetry run python examples/bug_world.py
poetry run python examples/grasping_robot.py
```

## Grasping robot

The grasping simulation follows a ball approaching a stationary robot. Its
distance and touch readings pass through independently timed qUnits, and the
resulting actuator signal closes the gripper. The public example is composed
from the world, the complete Redis-connected robot, and the live view below.

```{image} ../notebooks/07_imgs/grasping_live_world.png
:alt: Live grasping simulation with an approaching blue ball and stationary robot
:align: center
:width: 720px
```

```{eval-rst}
.. autoclass:: qrobot_simulator.grasping_robot.GraspingWorld
   :members:

.. autoclass:: qrobot_simulator.grasping_robot.GraspingRobot
   :members:

.. autoclass:: qrobot_simulator.grasping_robot.GraspingWorldLiveView
   :members:
```

## Bug world

The bug simulation places the qBrain-controlled robot in a mobile ecosystem
with blue prey and a red predator. Sensor readings and five behavioral
actuators form a closed loop between the chessboard world and the complete
bug robot; the internal prey and predator bodies remain implementation
details of the world.

```{image} ../notebooks/08_imgs/bug_live_world.png
:alt: Live bug-world simulation with the qBrain robot, blue prey, and red predator
:align: center
:width: 720px
```

```{eval-rst}
.. autoclass:: qrobot_simulator.bug_world.BugWorld
   :members:

.. autoclass:: qrobot_simulator.bug_world.BugRobot
   :members:

.. autoclass:: qrobot_simulator.bug_world.BugWorldLiveView
   :members:
```
