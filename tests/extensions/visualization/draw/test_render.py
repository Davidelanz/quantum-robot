import networkx as nx
import pytest

from qrobot_visualization import draw
from qrobot_visualization.draw.layout import node_positions


def test_draw_adds_architecture_blocks() -> None:
    graph = nx.DiGraph()
    graph.add_node("sensor", **{"class": "SensorialUnit"})
    graph.add_node("processor", **{"class": "QUnit"})
    graph.add_node("actuator", **{"class": "ActuatorUnit"})
    graph.add_edges_from([("sensor", "processor"), ("processor", "actuator")])

    figure = draw(graph)

    annotations = figure.to_dict()["layout"]["annotations"]
    labels = [annotation["text"] for annotation in annotations if annotation["text"]]
    assert labels == [
        "<b>Sensorial</b>",
        "<b>Q-Brain</b>",
        "<b>Actuators</b>",
    ]
    arrows = [annotation for annotation in annotations if annotation["showarrow"]]
    assert len(arrows) == len(graph.edges)
    assert {arrow["arrowcolor"] for arrow in arrows} == {"#315a9e", "#3f8a3c"}
    positions = node_positions(graph)
    assert [arrow["x"] for arrow in arrows] == pytest.approx(
        [positions["processor"][0] - 0.2, positions["actuator"][0] - 0.2]
    )
