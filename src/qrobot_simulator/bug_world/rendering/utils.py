"""Matplotlib graphics creation and update functions for the bug world."""

from dataclasses import dataclass
from math import cos, degrees, radians, sin

from matplotlib.axes import Axes
from matplotlib.lines import Line2D
from matplotlib.patches import Circle, Rectangle, Wedge
from matplotlib.text import Text

from ..robots.base import Robot
from ..world import WORLD_CONFIG, BugWorld, eye_response_strength
from .config import RENDERING_CONFIG


@dataclass(frozen=True)
class RobotGraphics:
    """Group the graphics representing one robot.

    :param body: Circular body patch.
    :param heading: Line indicating the robot heading.
    :param label: Text displaying the robot name.
    """

    body: Circle
    heading: Line2D
    label: Text


@dataclass(frozen=True)
class ConeCell:
    """Describe one annular sector in the eye-sensitivity field.

    :param patch: Wedge drawn for this field cell.
    :param eye_angle: Eye-ray offset in radians.
    :param start_angle: Cell start relative to the eye ray, in degrees.
    :param end_angle: Cell end relative to the eye ray, in degrees.
    """

    patch: Wedge
    eye_angle: float
    start_angle: float
    end_angle: float


@dataclass(frozen=True)
class EyeFieldGraphics:
    """Group sensitivity cells and centre-line guides for both eyes.

    :param cells: Annular sectors approximating eye sensitivity.
    :param centre_lines: Guides marking the two eye-ray centres.
    """

    cells: tuple[ConeCell, ...]
    centre_lines: tuple[Line2D, ...]


@dataclass(frozen=True)
class TextOverlays:
    """Group the dynamic status and score labels.

    :param status: Current bug behavior and elapsed-time label.
    :param score: Prey and predator bite counters.
    """

    status: Text
    score: Text


# Board graphics


def draw_checkerboard(axis: Axes, columns: int, rows: int, cell_size: float) -> None:
    """Draw a checkerboard background.

    :param axis: Matplotlib axes receiving the squares.
    :param columns: Number of horizontal cells.
    :param rows: Number of vertical cells.
    :param cell_size: Width and height of each cell in world units.
    """
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


def create_robot_graphics(axis: Axes, robot: Robot) -> RobotGraphics:
    """Create the graphics for one robot.

    :param axis: Matplotlib axes receiving the graphics.
    :param robot: Robot whose body, heading, and name are drawn.
    :returns: Graphics handles used for later updates.
    """
    body = Circle(
        (robot.x, robot.y),
        robot.radius,
        facecolor=robot.color,
        edgecolor=RENDERING_CONFIG.normal_outline_color,
        linewidth=RENDERING_CONFIG.normal_outline_width,
        zorder=RENDERING_CONFIG.robot_zorder,
    )
    axis.add_patch(body)
    heading = axis.plot(
        [], [], color=RENDERING_CONFIG.normal_outline_color, lw=RENDERING_CONFIG.robot_heading_width
    )[0]
    label = axis.text(
        robot.x,
        robot.y + RENDERING_CONFIG.robot_label_offset,
        robot.name,
        ha="center",
        fontsize=RENDERING_CONFIG.robot_label_size,
    )
    graphics = RobotGraphics(body, heading, label)
    update_robot_graphics(graphics, robot, biting=False)
    return graphics


def update_robot_graphics(graphics: RobotGraphics, robot: Robot, biting: bool) -> None:
    """Update one robot's existing graphics.

    :param graphics: Graphics handles created for the robot.
    :param robot: Robot providing the current pose.
    :param biting: Use the active-bite outline when true.
    """
    graphics.body.center = (robot.x, robot.y)
    graphics.body.set_edgecolor(
        RENDERING_CONFIG.bite_outline_color if biting else RENDERING_CONFIG.normal_outline_color
    )
    graphics.body.set_linewidth(
        RENDERING_CONFIG.bite_outline_width if biting else RENDERING_CONFIG.normal_outline_width
    )
    graphics.heading.set_data(
        [robot.x, robot.x + RENDERING_CONFIG.heading_line_length * cos(robot.heading)],
        [robot.y, robot.y + RENDERING_CONFIG.heading_line_length * sin(robot.heading)],
    )
    graphics.label.set_position((robot.x, robot.y + RENDERING_CONFIG.robot_label_offset))


# Sensor graphics


def create_eye_field(axis: Axes) -> EyeFieldGraphics:
    """Create the stereo eye-sensitivity field and ray guides.

    :param axis: Matplotlib axes receiving the graphics.
    :returns: Eye-field graphics handles used for later updates.
    """
    cells = tuple(_create_cone_cells(axis))
    colors = (
        RENDERING_CONFIG.left_eye_color,
        RENDERING_CONFIG.right_eye_color,
    )
    centre_lines = tuple(
        axis.plot(
            [],
            [],
            "--",
            color=color,
            lw=RENDERING_CONFIG.eye_guide_width,
            alpha=RENDERING_CONFIG.eye_guide_alpha,
        )[0]
        for color in colors
    )
    return EyeFieldGraphics(cells, centre_lines)


def update_eye_field(graphics: EyeFieldGraphics, robot: Robot) -> None:
    """Translate and rotate an eye field with its observing robot.

    :param graphics: Eye-field graphics to reposition.
    :param robot: Robot providing the current position and heading.
    """
    heading_degrees = degrees(robot.heading)
    for cell in graphics.cells:
        cell.patch.set_center((robot.x, robot.y))
        eye_heading = heading_degrees + degrees(cell.eye_angle)
        cell.patch.set_theta1(eye_heading + cell.start_angle)
        cell.patch.set_theta2(eye_heading + cell.end_angle)

    eye_angles = (
        WORLD_CONFIG.eye_angle,
        -WORLD_CONFIG.eye_angle,
    )
    for line, eye_angle in zip(graphics.centre_lines, eye_angles, strict=True):
        angle = robot.heading + eye_angle
        line.set_data(
            [robot.x, robot.x + RENDERING_CONFIG.cone_max_distance * cos(angle)],
            [robot.y, robot.y + RENDERING_CONFIG.cone_max_distance * sin(angle)],
        )


def create_proximity_wedge(axis: Axes) -> Wedge:
    """Create the frontal region of the binary proximity sensor.

    :param axis: Matplotlib axes receiving the wedge.
    :returns: Presence wedge used for later updates.
    """
    wedge = Wedge(
        (0, 0),
        WORLD_CONFIG.proximity_distance,
        -WORLD_CONFIG.proximity_half_angle_degrees,
        WORLD_CONFIG.proximity_half_angle_degrees,
        alpha=RENDERING_CONFIG.proximity_idle_alpha,
        color=RENDERING_CONFIG.proximity_color,
        zorder=RENDERING_CONFIG.proximity_zorder,
    )
    axis.add_patch(wedge)
    return wedge


def update_proximity_wedge(wedge: Wedge, robot: Robot, active: bool) -> None:
    """Update the position and activation of the proximity wedge.

    :param wedge: Existing proximity-sensor wedge.
    :param robot: Robot providing the current position and heading.
    :param active: Use active opacity when true.
    """
    heading = degrees(robot.heading)
    wedge.set_center((robot.x, robot.y))
    wedge.set_theta1(heading - WORLD_CONFIG.proximity_half_angle_degrees)
    wedge.set_theta2(heading + WORLD_CONFIG.proximity_half_angle_degrees)
    wedge.set_alpha(
        RENDERING_CONFIG.proximity_active_alpha if active else RENDERING_CONFIG.proximity_idle_alpha
    )


# Text overlays


def create_text_overlays(axis: Axes) -> TextOverlays:
    """Create the status, score, and eye-field legend labels.

    :param axis: Matplotlib axes receiving the labels.
    :returns: Dynamic text handles used for later updates.
    """
    status = axis.text(
        *RENDERING_CONFIG.status_position,
        "",
        transform=axis.transAxes,
        va="top",
        weight="bold",
    )
    score = axis.text(
        *RENDERING_CONFIG.score_position,
        "",
        transform=axis.transAxes,
        va="top",
        ha="right",
        weight="bold",
    )
    axis.text(
        *RENDERING_CONFIG.legend_position,
        RENDERING_CONFIG.legend_text,
        transform=axis.transAxes,
        fontsize=RENDERING_CONFIG.legend_size,
        color=RENDERING_CONFIG.legend_color,
    )
    return TextOverlays(status, score)


def update_text_overlays(overlays: TextOverlays, world: BugWorld) -> None:
    """Refresh behavior, elapsed-time, and bite-score labels.

    :param overlays: Dynamic labels to update.
    :param world: Current simulation state displayed by the labels.
    """
    overlays.status.set_text(f"{world.bug.behavior}   t={world.elapsed:5.1f}s")
    overlays.score.set_text(
        f"BITTEN PREY  {world.bitten_prey}     PREDATOR BITES  {world.predator_bites}"
    )


def _create_cone_cells(axis: Axes) -> list[ConeCell]:
    """Build eye-field cells using their midpoint response as fixed opacity."""
    radial_step = RENDERING_CONFIG.cone_max_distance / RENDERING_CONFIG.cone_radial_bands
    eye_styles = (
        (WORLD_CONFIG.eye_angle, RENDERING_CONFIG.left_eye_color),
        (-WORLD_CONFIG.eye_angle, RENDERING_CONFIG.right_eye_color),
    )
    cells: list[ConeCell] = []
    for eye_angle, color in eye_styles:
        for band in range(RENDERING_CONFIG.cone_radial_bands):
            inner_radius = band * radial_step
            outer_radius = (band + 1) * radial_step
            sample_distance = (inner_radius + outer_radius) / 2
            for start_angle in range(
                -RENDERING_CONFIG.cone_half_width_degrees,
                RENDERING_CONFIG.cone_half_width_degrees,
                RENDERING_CONFIG.cone_angular_step_degrees,
            ):
                end_angle = start_angle + RENDERING_CONFIG.cone_angular_step_degrees
                sample_angle = radians((start_angle + end_angle) / 2)
                strength = eye_response_strength(sample_distance, sample_angle, 0.0)
                patch = Wedge(
                    (0, 0),
                    outer_radius,
                    start_angle,
                    end_angle,
                    width=radial_step,
                    facecolor=color,
                    edgecolor="none",
                    alpha=RENDERING_CONFIG.cone_max_alpha * strength,
                    zorder=RENDERING_CONFIG.field_zorder,
                )
                axis.add_patch(patch)
                cells.append(ConeCell(patch, eye_angle, start_angle, end_angle))
    return cells
