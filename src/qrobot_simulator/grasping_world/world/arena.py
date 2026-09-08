"""Arena geometry for the grasping simulation."""

from dataclasses import dataclass

from .config import WORLD_CONFIG


@dataclass(frozen=True)
class GraspingArena:
    """Define the rectangular checkerboard arena."""

    width: float = WORLD_CONFIG.arena_width
    height: float = WORLD_CONFIG.arena_height
    cell_size: float = WORLD_CONFIG.arena_cell_size

    @property
    def bounds(self) -> tuple[float, float]:
        """Return the arena ``(width, height)`` in display units."""
        return self.width, self.height
