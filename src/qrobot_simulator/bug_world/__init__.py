"""Self-contained predator/prey world demonstrating an embodied qBrain."""

from .rendering import BugWorldLiveView
from .robots import BluePrey, BugRobot, RedPredator
from .world.bug_world import BugWorld

__all__ = [
    "BluePrey",
    "BugRobot",
    "BugWorld",
    "BugWorldLiveView",
    "RedPredator",
]
