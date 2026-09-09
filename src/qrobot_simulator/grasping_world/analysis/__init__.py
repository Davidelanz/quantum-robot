"""Tools for measuring controlled runs of the grasping-world demonstration.

The simulator itself provides the world, robots, sensors, and physical interaction.
This package adds predefined ball visits so the same situation can be presented
to different robots. Paper-specific trial generation and statistics remain outside
the simulator package.
"""

from .encounter import GraspingEncounter, MotionSegment, ProximityDisturbance, TimeInterval
from .controlled_world import ControlledGraspingWorld

__all__ = [
    "GraspingEncounter",
    "MotionSegment",
    "ProximityDisturbance",
    "TimeInterval",
    "ControlledGraspingWorld",
]
