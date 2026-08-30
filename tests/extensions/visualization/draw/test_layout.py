import networkx as nx
import plotly.graph_objects as go
import pytest

from qrobot_visualization.draw.layout import (
    add_group_blocks,
    figure_height,
    figure_layout,
    node_generations,
    node_group,
    node_positions,
    node_role,
)


def layered_graph() -> nx.DiGraph:
    graph = nx.DiGraph()
    graph.add_node("sensor", **{"class": "SensorialUnit"})
    graph.add_node("perceptual", **{"class": "QUnit"})
    graph.add_node("cognitive", **{"class": "QUnit"})
    graph.add_node("actuator", **{"class": "ActuatorUnit"})
    graph.add_edges_from(
        [("sensor", "perceptual"), ("perceptual", "cognitive"), ("cognitive", "actuator")]
    )
    return graph


def test_node_group_uses_published_class() -> None:
    graph = layered_graph()

    assert [node_group(graph, node) for node in graph] == [
        "sensorial",
        "qbrain",
        "qbrain",
        "actuator",
    ]


def test_node_generations_follow_longest_path() -> None:
    assert node_generations(layered_graph()) == {
        "sensor": 0,
        "perceptual": 1,
        "cognitive": 2,
        "actuator": 3,
    }


def test_node_role_distinguishes_perception_and_cognition() -> None:
    graph = layered_graph()

    assert node_role(graph, "perceptual") == "perceptual"
    assert node_role(graph, "cognitive") == "cognitive"


def test_node_positions_place_architecture_left_to_right() -> None:
    positions = node_positions(layered_graph())

    x_values = [positions[node][0] for node in ("sensor", "perceptual", "cognitive", "actuator")]
    assert x_values == sorted(x_values)
    differences = [right - left for left, right in zip(x_values, x_values[1:])]
    assert differences == pytest.approx([x_values[1]] * 3)


def test_figure_height_is_bounded_for_large_architectures() -> None:
    graph = layered_graph()
    for index in range(8):
        graph.add_node(f"sensor-{index}", **{"class": "SensorialUnit"})

    assert figure_height(graph) <= 760


def test_figure_layout_leaves_width_to_its_container() -> None:
    layout = figure_layout(layered_graph()).to_plotly_json()

    assert layout["autosize"] is True
    assert "width" not in layout


def test_group_blocks_leave_clearance_above_top_node() -> None:
    graph = layered_graph()
    positions = node_positions(graph)
    figure = go.Figure()

    add_group_blocks(figure, graph, positions)

    top_node = max(position[1] for position in positions.values())
    shapes = figure.to_dict()["layout"]["shapes"]
    annotations = figure.to_dict()["layout"]["annotations"]
    assert [shape["y1"] for shape in shapes] == pytest.approx([top_node + 1.2] * 3)
    assert [annotation["y"] for annotation in annotations] == pytest.approx([top_node + 1.2] * 3)
