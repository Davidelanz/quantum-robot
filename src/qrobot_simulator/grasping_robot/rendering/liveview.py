"""Persistent Matplotlib view for the live grasping encounter."""

from pathlib import Path

import matplotlib.pyplot as plt

from ..robots import GraspingSignals
from ..world import GraspingArena, GraspingWorld
from .config import RENDERING_CONFIG
from .utils import (
    create_robot_graphics,
    create_sensor_graphics,
    create_text_overlays,
    draw_checkerboard,
    update_robot_graphics,
    update_sensor_graphics,
    update_text_overlays,
)


class GraspingWorldLiveView:
    """Display a persistent view of the gripper encounter and qBrain state."""

    def __init__(self, arena: GraspingArena, interactive: bool = True) -> None:
        """Create the figure and its static graphics.

        :param arena: Arena whose dimensions define the axes.
        :param interactive: Enable GUI updates when true.
        """
        self._interactive = interactive
        if interactive:
            plt.ion()
        self.figure, self.axis = plt.subplots(
            num=RENDERING_CONFIG.figure_name,
            figsize=RENDERING_CONFIG.figure_size,
        )
        self._setup(arena)
        if interactive:
            plt.show(block=False)

    # Public view lifecycle

    @property
    def is_open(self) -> bool:
        """Return whether the Matplotlib figure still exists.

        :returns: True while the view's figure remains open.
        """
        return plt.fignum_exists(self.figure.number)

    def update(
        self,
        world: GraspingWorld,
        signals: GraspingSignals | None = None,
        phase: str = "RUNNING",
    ) -> None:
        """Refresh physical geometry and observable qBrain values.

        :param world: Current simulation state to display.
        :param signals: Latest observable qBrain outputs, when available.
        :param phase: Short label describing the simulation phase.
        """
        update_robot_graphics(self._robot_graphics, world)
        update_sensor_graphics(self._sensor_graphics, world)
        update_text_overlays(self._text_overlays, world, signals, phase)
        self._flush_canvas()

    def save(self, path: Path) -> Path:
        """Save the current frame to an image.

        Parent directories are created when needed.

        :param path: Destination image path.
        :returns: Destination path after the figure is saved.
        """
        path.parent.mkdir(parents=True, exist_ok=True)
        self.figure.savefig(path, dpi=RENDERING_CONFIG.save_dpi, bbox_inches="tight")
        return path

    def close(self) -> None:
        """Close the Matplotlib figure owned by this view."""
        plt.close(self.figure)

    # Internal figure management

    def _setup(self, arena: GraspingArena) -> None:
        """Draw static content and create the dynamic graphics."""
        draw_checkerboard(self.axis, arena.width, arena.height, arena.cell_size)
        self.axis.set(
            xlim=(0, arena.width),
            ylim=(0, arena.height),
            aspect="equal",
            title=RENDERING_CONFIG.axis_title,
            xlabel=RENDERING_CONFIG.axis_x_label,
            ylabel=RENDERING_CONFIG.axis_y_label,
        )
        self._robot_graphics = create_robot_graphics(self.axis)
        self._sensor_graphics = create_sensor_graphics(self.axis)
        self._text_overlays = create_text_overlays(self.axis)

    def _flush_canvas(self) -> None:
        """Draw one interactive frame; do nothing for headless views."""
        if self._interactive:
            self.figure.canvas.draw_idle()
            self.figure.canvas.flush_events()
            plt.pause(RENDERING_CONFIG.canvas_pause)
