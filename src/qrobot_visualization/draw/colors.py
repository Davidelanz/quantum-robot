"""Colors for qBrain figures."""

from matplotlib import colors, colormaps

SENSORIAL_COLOR = "#cbd5ff"
PERCEPTUAL_COLOR = "#cbd5ff"
COGNITIVE_COLOR = "#ffedb0"
ACTUATOR_COLOR = "#cfe8cb"

PERCEPTUAL_EDGE_COLOR = "#315a9e"
COGNITIVE_EDGE_COLOR = "#b8860b"
ACTUATOR_EDGE_COLOR = "#3f8a3c"

NODE_COLORS = {
    "sensorial": SENSORIAL_COLOR,
    "perceptual": PERCEPTUAL_COLOR,
    "cognitive": COGNITIVE_COLOR,
    "actuator": ACTUATOR_COLOR,
}

EDGE_COLORS = {
    "perceptual": PERCEPTUAL_EDGE_COLOR,
    "cognitive": COGNITIVE_EDGE_COLOR,
    "actuator": ACTUATOR_EDGE_COLOR,
}


def output_color(value: float) -> str:
    """Map a normalized output to a hexadecimal ``coolwarm`` color."""
    color_map: colors.Colormap = colormaps["coolwarm"]
    return colors.to_hex(color_map(value))
