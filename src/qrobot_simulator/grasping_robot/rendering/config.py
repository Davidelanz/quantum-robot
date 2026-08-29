"""Visual configuration for the Matplotlib grasping-world renderer."""

from dataclasses import dataclass


@dataclass(frozen=True)
class RenderingConfig:
    """Configure the appearance and layout of the Matplotlib live view."""

    # Figure lifecycle and labels
    figure_size: tuple[float, float] = (9.0, 5.0)
    save_dpi: int = 160
    canvas_pause: float = 0.001
    figure_name: str = "qrobot grasping world"
    axis_title: str = "Live qBrain object-grasping world"
    axis_x_label: str = "arena x"
    axis_y_label: str = "arena y"
    # Gripper body and jaws
    robot_edge_color: str = "#24170f"
    robot_edge_width: float = 2.0
    open_jaw_gap: float = 0.72
    closed_jaw_gap: float = 0.27
    jaw_base_offset_y: float = 0.42
    jaw_normal_width: float = 3.0
    jaw_contact_width: float = 6.0
    # Touch feedback
    touch_pad_radius: float = 0.10
    touch_pad_idle_color: str = "#d9d9d9"
    touch_pad_active_color: str = "#19a64a"
    touch_pad_active_edge: str = "#08752e"
    touch_pad_idle_width: float = 1.2
    touch_pad_active_width: float = 2.5
    # Sensor and grippable regions
    sensor_color: str = "#e68a35"
    sensor_text_color: str = "#a85a16"
    grip_region_color: str = "#4caf50"
    grip_region_edge: str = "#247a28"
    # Board and ball-prey appearance
    board_light_shade: float = 0.94
    board_dark_shade: float = 0.86
    ball_edge_color: str = "#173f70"
    sensor_half_height: float = 0.18
    grip_region_half_height: float = 0.28
    sensor_idle_alpha: float = 0.08
    sensor_signal_alpha: float = 0.30
    grip_region_alpha: float = 0.13
    sensor_boundary_width: float = 1.5
    sensor_label_offset: tuple[float, float] = (1.55, 0.42)
    grip_label_y_offset: float = -1.0
    annotation_size: int = 8
    # Status overlays
    status_box_alpha: float = 0.78
    status_box_edge: str = "#777777"
    # Drawing order
    board_zorder: float = 0.0
    sensor_zorder: float = 1.0
    boundary_zorder: float = 2.0
    robot_zorder: float = 3.0
    jaw_zorder: float = 4.0
    touch_pad_zorder: float = 5.0
    # Axes-relative overlay positions
    status_position: tuple[float, float] = (0.02, 0.97)
    physical_state_position: tuple[float, float] = (0.02, 0.08)
    score_position: tuple[float, float] = (0.98, 0.08)
    brain_state_position: tuple[float, float] = (0.98, 0.97)


RENDERING_CONFIG = RenderingConfig()
