"""Public participants and view of the predator-prey example."""

from .rendering.liveview import BugWorldLiveView
from .robots.classical_bug import ClassicalBug
from .robots.quantum_bug import QuantumBug
from .world.bug_world import BugWorld

__all__ = ["BugWorld", "BugWorldLiveView", "ClassicalBug", "QuantumBug"]
