"""Persistent Matplotlib view for the live bug ecosystem."""

from pathlib import Path

import matplotlib.pyplot as plt

from ..world import BugWorld, Chessboard
from .config import RENDERING_CONFIG
from .utils import (
    RobotGraphics,
    create_eye_field,
    create_proximity_wedge,
    create_robot_graphics,
    create_text_overlays,
    draw_checkerboard,
    update_eye_field,
    update_proximity_wedge,
    update_robot_graphics,
    update_text_overlays,
)


class BugWorldLiveView:
    """Display a persistent view of the world, sensors, and scores."""

    def __init__(self, board: Chessboard, interactive: bool = True) -> None:
        """Create the figure and its static graphics.

        :param board: Checkerboard whose dimensions define the axes.
        :param interactive: Enable GUI updates when true.
        """
        self._interactive = interactive
        if interactive:
            plt.ion()
        self.figure, self.axis = plt.subplots(
            num=RENDERING_CONFIG.figure_name,
            figsize=RENDERING_CONFIG.figure_size,
        )
        self._setup(board)
        if interactive:
            plt.show(block=False)

    # Public view lifecycle

    @property
    def is_open(self) -> bool:
        """Return whether the Matplotlib figure still exists.

        :returns: True while the view's figure remains open.
        """
        return plt.fignum_exists(self.figure.number)

    def update(self, world: BugWorld) -> None:
        """Refresh all graphics and labels from a world snapshot.

        :param world: Current simulation state to display.
        """
        for robot in world.robots:
            graphics = self._robots.get(robot.name)
            if graphics is None:
                graphics = create_robot_graphics(self.axis, robot)
                self._robots[robot.name] = graphics
            biting = (robot is world.bug and world.bug_biting) or (
                robot is world.predator and world.predator_biting
            )
            update_robot_graphics(graphics, robot, biting)

        update_eye_field(self._eye_field, world.bug)
        update_proximity_wedge(
            self._proximity,
            world.bug,
            active=bool(world.readings.get("proximity", 0.0)),
        )
        update_text_overlays(self._text_overlays, world)
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

    def _setup(self, board: Chessboard) -> None:
        """Draw static content and create the dynamic graphics."""
        draw_checkerboard(self.axis, board.columns, board.rows, board.cell_size)
        width, height = board.bounds
        self.axis.set(
            xlim=(0, width),
            ylim=(0, height),
            aspect="equal",
            title=RENDERING_CONFIG.axis_title,
            xlabel=RENDERING_CONFIG.axis_x_label,
            ylabel=RENDERING_CONFIG.axis_y_label,
        )
        self._robots: dict[str, RobotGraphics] = {}
        self._eye_field = create_eye_field(self.axis)
        self._proximity = create_proximity_wedge(self.axis)
        self._text_overlays = create_text_overlays(self.axis)

    def _flush_canvas(self) -> None:
        """Draw one interactive frame; do nothing for headless views."""
        if self._interactive:
            self.figure.canvas.draw_idle()
            self.figure.canvas.flush_events()
            plt.pause(RENDERING_CONFIG.canvas_pause)
