"""Robot bodies and autonomous policies used by :mod:`qrobot_simulator`."""

from .base import Robot
from .blue_prey import BluePrey
from .bug_robot import BugRobot
from .red_predator import RedPredator

__all__ = [
    "BluePrey",
    "BugRobot",
    "RedPredator",
    "Robot",
]
