from qrobot_visualization.draw.colors import output_color


def test_output_color_returns_hex_color() -> None:
    assert output_color(0.5).startswith("#")
