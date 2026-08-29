"""World state and configuration for the bug-world simulation."""

from .bug_world import BugWorld, Chessboard, eye_response_strength
from .config import WORLD_CONFIG, WorldConfig

__all__ = ["BugWorld", "Chessboard", "WORLD_CONFIG", "WorldConfig", "eye_response_strength"]
