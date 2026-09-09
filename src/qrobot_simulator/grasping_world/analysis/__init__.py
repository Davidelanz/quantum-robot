"""Tools for measuring controlled runs of the grasping-world demonstration.

The simulator itself provides the world, robots, sensors, and physical interaction.
This package adds the predefined ball visits and recording needed to study that
behavior analytically. It can repeat the same visit for different robots, retain
the raw sensor and action sequence, identify physical events, and calculate one
encounter result. Paper-specific trial generation and statistics remain outside
the simulator package.
"""

from .encounter import GraspingEncounter, MotionSegment, ProximityDisturbance, TimeInterval
from .recording import (
    GraspingEvent,
    GraspingOutcome,
    GraspingRunMetadata,
    GraspingRunRecord,
    GraspingSample,
    summarize_encounter,
)
from .runner import record_encounter
from .controlled_world import ControlledGraspingWorld

__all__ = [
    "GraspingEncounter",
    "GraspingEvent",
    "GraspingOutcome",
    "GraspingRunMetadata",
    "GraspingRunRecord",
    "GraspingSample",
    "MotionSegment",
    "ProximityDisturbance",
    "TimeInterval",
    "ControlledGraspingWorld",
    "record_encounter",
    "summarize_encounter",
]
