"""Tests for live dashboard figure formatting."""

import networkx as nx
import plotly.graph_objects as go
import pytest

from qrobot_dashboard.figure import (
    base_figure,
    build_live_figure,
    display_name,
    network_structure,
    node_hover_text,
    node_label,
    output_label,
    output_value,
    signal_strength,
    style_live_figure,
    topology_key,
)
from qrobot_visualization import draw


@pytest.mark.parametrize(
    ("raw", "expected"),
    [("0.5", 0.5), (1, 1.0), (None, None), ("invalid", None), ("nan", None)],
)
def test_output_value_accepts_only_finite_scalars(raw: object, expected: float | None) -> None:
    """Redis values become floats only when they are valid and finite."""
    assert output_value(raw) == expected


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        (None, "—"),
        ("0", "0"),
        ("0.666666666666", "0.67"),
        ("0.0001", "<0.01"),
        ("-0.0001", "-<0.01"),
    ],
)
def test_output_label_is_compact_without_hiding_small_values(raw: object, expected: str) -> None:
    """Visible labels distinguish tiny signals from zero."""
    assert output_label(raw) == expected


@pytest.mark.parametrize(
    ("raw", "expected"),
    [(None, 0.0), ("-1", 0.0), ("0.4", 0.4), ("2", 1.0)],
)
def test_signal_strength_is_clamped(raw: object, expected: float) -> None:
    """Connection styling always receives a value between zero and one."""
    assert signal_strength(raw) == expected


def test_node_text_is_short_safe_and_precise_on_hover() -> None:
    """Visible text is compact while hover text retains runtime details."""
    node_id = "sensor<script>-abcdef"
    assert display_name(node_id) == "sensor&lt;script&gt;"
    assert node_label(node_id, {"class": "SensorialUnit", "output": "0.25"}) == (
        "<b>sensor&lt;script&gt;</b><br>output: 0.25"
    )
    assert node_label("processor", {"class": "QUnit", "output": "1"}).endswith("burst: 1")
    assert node_hover_text(node_id, None).endswith("Output: not yet published")
    assert "0.250000" in node_hover_text(node_id, "0.250000")


def test_topology_key_ignores_runtime_outputs() -> None:
    """Signal updates preserve the user's Plotly viewport."""
    network = nx.DiGraph([("sensor", "processor")])
    first = topology_key(network)
    network.nodes["sensor"]["output"] = "1"
    assert topology_key(network) == first


def test_network_structure_contains_only_static_drawing_data() -> None:
    """The figure cache excludes outputs but distinguishes unit roles."""
    network = nx.DiGraph()
    network.add_node("sensor", **{"class": "SensorialUnit", "output": "0"})
    network.add_node("processor", **{"class": "QUnit", "output": "1"})
    network.add_edge("sensor", "processor")
    first = network_structure(network)
    network.nodes["sensor"]["output"] = "1"
    assert network_structure(network) == first
    assert first == (
        (("processor", "QUnit"), ("sensor", "SensorialUnit")),
        (("sensor", "processor"),),
    )


def test_build_live_figure_reuses_static_geometry() -> None:
    """Repeated signal updates share the cached architecture drawing."""
    base_figure.cache_clear()
    network = nx.DiGraph()
    network.add_node("sensor", **{"class": "SensorialUnit", "output": "0"})
    first = build_live_figure(network)
    cache_after_first = base_figure.cache_info()
    network.nodes["sensor"]["output"] = "1"
    second = build_live_figure(network)
    cache_after_second = base_figure.cache_info()
    assert cache_after_first.misses == 1
    assert cache_after_second.hits == 1
    assert first is not second
    assert first.data[-1].text != second.data[-1].text


def test_style_live_figure_moves_outputs_from_edges_to_nodes() -> None:
    """The live view uses line strength, concise labels, and exact hover text."""
    network = nx.DiGraph()
    network.add_node("sensor-abcdef", **{"class": "SensorialUnit", "output": "0.75"})
    network.add_node("processor", **{"class": "QUnit"})
    network.add_edge("sensor-abcdef", "processor", output="0.75")
    figure = style_live_figure(draw(network), network)

    assert isinstance(figure, go.Figure)
    assert figure.data[0].mode == "lines"
    assert figure.data[0].text is None
    assert figure.data[0].line.width == pytest.approx(3.25)
    assert "<b>sensor</b><br>output: 0.75" in figure.data[-1].text
    assert any("0.75" in text for text in figure.data[-2].hovertext)
    assert figure.layout.uirevision == topology_key(network)
