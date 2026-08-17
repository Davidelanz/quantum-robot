# Embodied simulators

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
