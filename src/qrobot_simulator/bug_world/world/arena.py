"""Checkerboard geometry used by the bug world and live view."""

from dataclasses import dataclass

from .config import WORLD_CONFIG


@dataclass(frozen=True)
class Chessboard:
    """Define the rectangular checkerboard arena.

    :param columns: Number of horizontal cells.
    :param rows: Number of vertical cells.
    :param cell_size: Width and height of each cell in world units.
    """

    columns: int = WORLD_CONFIG.board_columns
    rows: int = WORLD_CONFIG.board_rows
    cell_size: float = WORLD_CONFIG.board_cell_size

    @property
    def bounds(self) -> tuple[float, float]:
        """Return the arena width and height in world units."""
        return self.columns * self.cell_size, self.rows * self.cell_size
