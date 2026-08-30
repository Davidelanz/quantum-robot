import networkx as nx
import numpy as np
import pytest

from qrobot_visualization.draw.traces import edge_coordinates, node_text, node_text_trace


def test_node_text_summarizes_unit_configuration() -> None:
    text = node_text(
        "processor-id",
        {
            "name": "processor",
            "class": "QUnit",
            "model": "AngularModel (n: 1, τ: 10)",
            "burst": "ZeroBurst",
            "query": [1.0],
            "sampling_period": 0.1,
        },
    )

    assert "AngularModel (n: 1, τ: 10)" in text
    assert "ZeroBurst" in text
    assert "query: [1.0]" in text
    assert "Tₛ: 0.1" in text
    assert "model:" not in text
    assert "burst:" not in text
    assert " · " not in text
    assert text.count("<br>") == 4


def test_edge_coordinates_stop_at_node_boundaries() -> None:
    x_values, y_values = edge_coordinates(np.array([0.0, 0.0]), np.array([4.2, 1.0]))

    assert x_values[0] == 0.2
    assert x_values[-1] == 4.0
    assert y_values[-1] == 1.0


def test_node_text_trace_offsets_labels_below_markers() -> None:
    graph = nx.DiGraph()
    graph.add_node("sensor", name="sensor")
    positions = {"sensor": np.array([1.0, 2.0])}

    trace = node_text_trace(graph, positions, font_size=11, vertical_offset=0.4)

    assert list(trace.x) == [1.0]
    assert list(trace.y) == pytest.approx([1.6])
    assert trace.mode == "text"
