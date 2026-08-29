"""Matplotlib graphics creation and update functions for the grasping world."""

from dataclasses import dataclass

from matplotlib.axes import Axes
from matplotlib.lines import Line2D
from matplotlib.patches import Circle, Rectangle
from matplotlib.text import Text

from ..robots import GraspingSignals
from ..robots.config import BALL_PREY_CONFIG, GRIPPER_ROBOT_CONFIG
from ..world import WORLD_CONFIG, GraspingWorld
from .config import RENDERING_CONFIG


@dataclass(frozen=True)
class RobotGraphics:
    """Group the graphics representing the gripper and ball prey.

    :param body: Rectangular body of the gripper robot.
    :param jaws: Lines representing the upper and lower jaws.
    :param touch_pads: Contact switches at the jaw tips.
    :param ball_prey: Circular body of the ball prey.
    """

    body: Rectangle
    jaws: tuple[Line2D, Line2D]
    touch_pads: tuple[Circle, Circle]
    ball_prey: Circle


@dataclass(frozen=True)
class SensorGraphics:
    """Group the dynamic graphics of the proximity sensor.

    :param proximity_region: Colored sensor-range rectangle.
    :param distance_line: Line joining the sensor and ball prey.
    """

    proximity_region: Rectangle
    distance_line: Line2D


@dataclass(frozen=True)
class TextOverlays:
    """Group the dynamic labels describing state, scores, and signals.

    :param status: Current phase, time, and measured distance.
    :param physical_state: Gripper and touch-switch state.
    :param score: Correct, missed, and empty grip counters.
    :param brain_state: Latest sensor, qUnit, and actuator signals.
    """

    status: Text
    physical_state: Text
    score: Text
    brain_state: Text


# Board graphics


def draw_checkerboard(axis: Axes, width: float, height: float, cell_size: float) -> None:
    """Draw a checkerboard background.

    :param axis: Matplotlib axes receiving the squares.
    :param width: Board width in world units.
    :param height: Board height in world units.
    :param cell_size: Width and height of each square.
    """
    rows = int(height / cell_size)
    columns = int(width / cell_size)
    for row in range(rows):
        for column in range(columns):
            shade = (
                RENDERING_CONFIG.board_light_shade
                if (row + column) % 2
                else RENDERING_CONFIG.board_dark_shade
            )
            axis.add_patch(
                Rectangle(
                    (column * cell_size, row * cell_size),
                    cell_size,
                    cell_size,
                    color=str(shade),
                    zorder=RENDERING_CONFIG.board_zorder,
                )
            )


# Robot graphics


def create_robot_graphics(axis: Axes) -> RobotGraphics:
    """Create the gripper robot and ball-prey graphics.

    :param axis: Matplotlib axes receiving the graphics.
    :returns: Graphics handles used for later updates.
    """
    body = Rectangle(
        (0, 0),
        2 * GRIPPER_ROBOT_CONFIG.half_width,
        2 * GRIPPER_ROBOT_CONFIG.half_height,
        facecolor=GRIPPER_ROBOT_CONFIG.color,
        edgecolor=RENDERING_CONFIG.robot_edge_color,
        linewidth=RENDERING_CONFIG.robot_edge_width,
        zorder=RENDERING_CONFIG.robot_zorder,
    )
    axis.add_patch(body)
    jaws = (
        axis.plot([], [], zorder=RENDERING_CONFIG.jaw_zorder)[0],
        axis.plot([], [], zorder=RENDERING_CONFIG.jaw_zorder)[0],
    )
    touch_pads = (
        Circle(
            (0, 0),
            RENDERING_CONFIG.touch_pad_radius,
            facecolor=RENDERING_CONFIG.touch_pad_idle_color,
            zorder=RENDERING_CONFIG.touch_pad_zorder,
        ),
        Circle(
            (0, 0),
            RENDERING_CONFIG.touch_pad_radius,
            facecolor=RENDERING_CONFIG.touch_pad_idle_color,
            zorder=RENDERING_CONFIG.touch_pad_zorder,
        ),
    )
    for pad in touch_pads:
        axis.add_patch(pad)
    ball_prey = Circle(
        (0, 0),
        BALL_PREY_CONFIG.radius,
        color=BALL_PREY_CONFIG.color,
        ec=RENDERING_CONFIG.ball_edge_color,
        zorder=RENDERING_CONFIG.jaw_zorder,
    )
    axis.add_patch(ball_prey)
    return RobotGraphics(body, jaws, touch_pads, ball_prey)


def update_robot_graphics(graphics: RobotGraphics, world: GraspingWorld) -> None:
    """Update the gripper and ball-prey graphics from a world snapshot.

    :param graphics: Graphics handles created for the robots.
    :param world: Current physical simulation state.
    """
    robot = world.robot
    graphics.body.set_xy(
        (
            robot.x - GRIPPER_ROBOT_CONFIG.half_width,
            robot.y - GRIPPER_ROBOT_CONFIG.half_height,
        )
    )
    graphics.ball_prey.center = (world.ball.x, world.ball.y)
    gap = RENDERING_CONFIG.closed_jaw_gap if robot.gripper_closed else RENDERING_CONFIG.open_jaw_gap
    sensor_x = robot.x + WORLD_CONFIG.sensor_offset_x
    base_x = sensor_x + WORLD_CONFIG.minimum_distance * WORLD_CONFIG.ball_distance_scale
    tip_x = sensor_x + WORLD_CONFIG.grippable_distance * WORLD_CONFIG.ball_distance_scale
    for jaw, pad, direction in zip(graphics.jaws, graphics.touch_pads, (1, -1), strict=True):
        tip_y = robot.y + direction * gap
        jaw.set_data(
            [base_x, tip_x],
            [robot.y + direction * RENDERING_CONFIG.jaw_base_offset_y, tip_y],
        )
        jaw.set_color(
            RENDERING_CONFIG.touch_pad_active_color
            if world.touch_pressed
            else RENDERING_CONFIG.robot_edge_color
        )
        jaw.set_linewidth(
            RENDERING_CONFIG.jaw_contact_width
            if world.touch_pressed
            else RENDERING_CONFIG.jaw_normal_width
        )
        pad.center = (tip_x, tip_y)
        pad.set_facecolor(
            RENDERING_CONFIG.touch_pad_active_color
            if world.touch_pressed
            else RENDERING_CONFIG.touch_pad_idle_color
        )
        pad.set_edgecolor(
            RENDERING_CONFIG.touch_pad_active_edge
            if world.touch_pressed
            else RENDERING_CONFIG.robot_edge_color
        )
        pad.set_linewidth(
            RENDERING_CONFIG.touch_pad_active_width
            if world.touch_pressed
            else RENDERING_CONFIG.touch_pad_idle_width
        )


# Sensor graphics


def create_sensor_graphics(axis: Axes) -> SensorGraphics:
    """Create the proximity range, grippable zone, and annotations.

    :param axis: Matplotlib axes receiving the graphics.
    :returns: Dynamic sensor graphics handles.
    """
    robot_x = GRIPPER_ROBOT_CONFIG.x
    robot_y = GRIPPER_ROBOT_CONFIG.y
    origin_x = robot_x + WORLD_CONFIG.sensor_offset_x
    proximity_region = Rectangle(
        (origin_x, robot_y - RENDERING_CONFIG.sensor_half_height),
        WORLD_CONFIG.far_distance * WORLD_CONFIG.ball_distance_scale,
        2 * RENDERING_CONFIG.sensor_half_height,
        color=RENDERING_CONFIG.sensor_color,
        alpha=RENDERING_CONFIG.sensor_idle_alpha,
        zorder=RENDERING_CONFIG.sensor_zorder,
    )
    axis.add_patch(proximity_region)
    grip_x = origin_x + WORLD_CONFIG.minimum_distance * WORLD_CONFIG.ball_distance_scale
    grip_width = (
        WORLD_CONFIG.grippable_distance - WORLD_CONFIG.minimum_distance
    ) * WORLD_CONFIG.ball_distance_scale
    axis.add_patch(
        Rectangle(
            (grip_x, robot_y - RENDERING_CONFIG.grip_region_half_height),
            grip_width,
            2 * RENDERING_CONFIG.grip_region_half_height,
            facecolor=RENDERING_CONFIG.grip_region_color,
            edgecolor=RENDERING_CONFIG.grip_region_edge,
            alpha=RENDERING_CONFIG.grip_region_alpha,
            linestyle="--",
            zorder=RENDERING_CONFIG.sensor_zorder,
        )
    )
    axis.axvline(
        origin_x + WORLD_CONFIG.far_distance * WORLD_CONFIG.ball_distance_scale,
        color=RENDERING_CONFIG.sensor_text_color,
        linestyle=":",
        linewidth=RENDERING_CONFIG.sensor_boundary_width,
        zorder=RENDERING_CONFIG.boundary_zorder,
    )
    distance_line = axis.plot([], [], "--", color=RENDERING_CONFIG.sensor_color)[0]
    axis.text(
        origin_x + RENDERING_CONFIG.sensor_label_offset[0],
        robot_y + RENDERING_CONFIG.sensor_label_offset[1],
        "PROXIMITY SENSOR RANGE",
        color=RENDERING_CONFIG.sensor_text_color,
        fontsize=RENDERING_CONFIG.annotation_size,
        weight="bold",
    )
    midpoint = (WORLD_CONFIG.minimum_distance + WORLD_CONFIG.grippable_distance) / 2
    axis.text(
        origin_x + midpoint * WORLD_CONFIG.ball_distance_scale,
        robot_y + RENDERING_CONFIG.grip_label_y_offset,
        f"GRIPPABLE AREA ({WORLD_CONFIG.minimum_distance:g}–"
        f"{WORLD_CONFIG.grippable_distance:g} cm)",
        color=RENDERING_CONFIG.robot_edge_color,
        fontsize=RENDERING_CONFIG.annotation_size,
        ha="center",
    )
    return SensorGraphics(proximity_region, distance_line)


def update_sensor_graphics(graphics: SensorGraphics, world: GraspingWorld) -> None:
    """Update measured distance and proximity-strength graphics.

    :param graphics: Dynamic sensor graphics handles.
    :param world: Current physical simulation state.
    """
    origin_x = world.robot.x + WORLD_CONFIG.sensor_offset_x
    graphics.proximity_region.set_xy(
        (origin_x, world.robot.y - RENDERING_CONFIG.sensor_half_height)
    )
    graphics.distance_line.set_data([origin_x, world.ball.x], [world.robot.y, world.ball.y])
    graphics.proximity_region.set_alpha(
        RENDERING_CONFIG.sensor_idle_alpha
        + RENDERING_CONFIG.sensor_signal_alpha * world.readings["proximity"]
    )


# Text graphics


def create_text_overlays(axis: Axes) -> TextOverlays:
    """Create labels updated each frame with state, scores, and signals.

    :param axis: Matplotlib axes receiving the labels.
    :returns: Text handles used for later updates.
    """
    status = axis.text(
        *RENDERING_CONFIG.status_position,
        "",
        transform=axis.transAxes,
        va="top",
        weight="bold",
    )
    physical_state = axis.text(
        *RENDERING_CONFIG.physical_state_position,
        "",
        transform=axis.transAxes,
        va="bottom",
        weight="bold",
    )
    box = {
        "facecolor": "white",
        "alpha": RENDERING_CONFIG.status_box_alpha,
        "edgecolor": RENDERING_CONFIG.status_box_edge,
    }
    score = axis.text(
        *RENDERING_CONFIG.score_position,
        "",
        transform=axis.transAxes,
        va="bottom",
        ha="right",
        family="monospace",
        weight="bold",
        bbox=box,
    )
    brain_state = axis.text(
        *RENDERING_CONFIG.brain_state_position,
        "",
        transform=axis.transAxes,
        va="top",
        ha="right",
        family="monospace",
        bbox=box,
    )
    return TextOverlays(status, physical_state, score, brain_state)


def update_text_overlays(
    graphics: TextOverlays,
    world: GraspingWorld,
    signals: GraspingSignals | None,
    phase: str,
) -> None:
    """Update state, scores, and qBrain signal labels.

    :param graphics: Text handles to update.
    :param world: Current physical simulation state.
    :param signals: Latest observable qBrain outputs, when available.
    :param phase: Short label describing the simulation phase.
    """
    signals = signals or GraspingSignals(None, None, None)
    gripper = "CLOSED" if world.robot.gripper_closed else "OPEN"
    touch = "PRESSED" if world.touch_pressed else "EMPTY"
    graphics.status.set_text(
        f"{phase}   t={world.elapsed:4.1f}s   distance={world.ball.distance:4.1f} cm"
    )
    graphics.physical_state.set_text(f"GRIPPER {gripper}\nTOUCH {touch}")
    graphics.score.set_text(
        "GRIP RESULTS\n"
        f"correct  {world.correct_grips}\n"
        f"missed   {world.missed_grips}\n"
        f"empty    {world.empty_grips}"
    )
    graphics.brain_state.set_text(
        "qBRAIN SIGNALS\n"
        f"proximity input  {world.readings['proximity']:.2f}\n"
        f"empty input      {world.readings['touch']:.2f}\n"
        f"proximity burst  {_signal_text(signals.proximity_burst)}\n"
        f"empty burst      {_signal_text(signals.empty_gripper_burst)}\n"
        f"actuator         {_signal_text(signals.gripper_activation)}"
    )


def _signal_text(value: float | None) -> str:
    """Format an unpublished signal distinctly from numeric zero."""
    return "warming" if value is None else f"{value:.2f}"
