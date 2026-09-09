"""Visual configuration for the Matplotlib bug-world renderer."""

from dataclasses import dataclass


@dataclass(frozen=True)
class RenderingConfig:
    """Configure colors, dimensions, labels, and drawing order.

    ``left_eye_color``, ``right_eye_color``, ``normal_outline_color``,
    ``bite_outline_color``, ``proximity_color``, ``legend_color``, and the two
    board shades define colors. The outline, eye-guide, heading, label, legend,
    cone, proximity, figure, and canvas fields control their corresponding
    sizes, alpha values, resolution, and refresh interval. ``figure_name``,
    ``axis_title``, ``axis_x_label``, ``axis_y_label``, and ``legend_text``
    supply visible text. The four ``*_zorder`` fields define drawing order,
    while ``status_position``, ``score_position``, and ``legend_position``
    locate text in normalized axes coordinates.
    """

    left_eye_color: str = "#2878d0"
    right_eye_color: str = "#e68a35"
    normal_outline_color: str = "#24170f"
    bite_outline_color: str = "#19a64a"
    normal_outline_width: float = 1.0
    bite_outline_width: float = 3.0
    cone_max_distance: float = 7.5
    cone_radial_bands: int = 8
    cone_half_width_degrees: int = 70
    cone_angular_step_degrees: int = 10
    cone_max_alpha: float = 0.18
    figure_size: tuple[float, float] = (9.0, 6.0)
    save_dpi: int = 160
    heading_line_length: float = 0.65
    robot_label_offset: float = 0.45
    proximity_active_alpha: float = 0.5
    proximity_idle_alpha: float = 0.12
    proximity_color: str = "#45a56a"
    board_light_shade: float = 0.94
    board_dark_shade: float = 0.86
    eye_guide_width: float = 1.2
    eye_guide_alpha: float = 0.65
    robot_heading_width: float = 2.0
    robot_label_size: int = 8
    canvas_pause: float = 0.001
    figure_name: str = "qrobot bug world"
    axis_title: str = "Live qBrain predator/prey world"
    axis_x_label: str = "arena x"
    axis_y_label: str = "arena y"
    board_zorder: float = 0.0
    field_zorder: float = 1.0
    proximity_zorder: float = 1.2
    robot_zorder: float = 3.0
    status_position: tuple[float, float] = (0.02, 0.98)
    score_position: tuple[float, float] = (0.98, 0.98)
    legend_position: tuple[float, float] = (0.02, 0.02)
    legend_size: int = 8
    legend_color: str = "#3f3f3f"
    legend_text: str = "blue: left eye   orange: right eye   opacity: sensitivity"


RENDERING_CONFIG = RenderingConfig()
