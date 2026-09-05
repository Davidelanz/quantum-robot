"""Compact live signal styling for dashboard network figures."""

import math
import re
from functools import lru_cache
from html import escape

import networkx as nx
import plotly.graph_objects as go
from qrobot_visualization import draw

UNIT_ID_SUFFIX = re.compile(r"-[0-9a-f]{6}$")
MIN_VISIBLE_SIGNAL = 0.01
NetworkStructure = tuple[tuple[tuple[str, str], ...], tuple[tuple[str, str], ...]]


def output_value(raw: object) -> float | None:
    """Parse a finite scalar output.

    Parameters
    ----------
    raw : object
        Published Redis value or another scalar-like value.

    Returns
    -------
    float or None
        Parsed finite value, or ``None`` when the value is absent or invalid.
    """
    try:
        value = float(str(raw))
    except (TypeError, ValueError):
        return None
    return value if math.isfinite(value) else None


def output_label(raw: object) -> str:
    """Format an output as a compact dashboard label.

    Parameters
    ----------
    raw : object
        Published Redis value or another scalar-like value.

    Returns
    -------
    str
        A label rounded to two decimal places. Small nonzero values remain
        visibly distinct from zero.
    """
    value = output_value(raw)
    if value is None:
        return "—"
    if 0 < value < MIN_VISIBLE_SIGNAL:
        return "<0.01"
    if -MIN_VISIBLE_SIGNAL < value < 0:
        return "-<0.01"
    return f"{value:.2f}".rstrip("0").rstrip(".")


def signal_strength(raw: object) -> float:
    """Clamp an output to the visual signal range.

    Parameters
    ----------
    raw : object
        Published output value.

    Returns
    -------
    float
        Value between zero and one used to style a connection.
    """
    value = output_value(raw)
    return min(1.0, max(0.0, value)) if value is not None else 0.0


def display_name(node_id: str) -> str:
    """Return a safe, stable label for a runtime unit ID.

    Parameters
    ----------
    node_id : str
        Unit ID, which may end in a random six-character hexadecimal suffix.

    Returns
    -------
    str
        HTML-escaped label without the runtime suffix.
    """
    return escape(UNIT_ID_SUFFIX.sub("", node_id))


def node_label(node_id: str, attributes: dict[str, object]) -> str:
    """Build the visible label for a live network node.

    Parameters
    ----------
    node_id : str
        Runtime unit ID.
    attributes : dict[str, object]
        Attributes published for the unit.

    Returns
    -------
    str
        Compact HTML label containing the unit name and output when available.
    """
    label = f"<b>{display_name(node_id)}</b>"
    raw = attributes.get("output")
    if raw is not None:
        kind = "burst" if attributes.get("class") == "QUnit" else "output"
        label += f"<br>{kind}: {escape(output_label(raw))}"
    return label


def node_hover_text(node_id: str, raw_output: object) -> str:
    """Build hover text retaining the exact published output.

    Parameters
    ----------
    node_id : str
        Full runtime unit ID.
    raw_output : object
        Exact output value, or ``None`` before the unit publishes one.

    Returns
    -------
    str
        HTML hover text safe to render in Plotly.
    """
    output = escape(str(raw_output)) if raw_output is not None else "not yet published"
    return f"{escape(node_id)}<br>Output: {output}"


def topology_key(network: nx.DiGraph) -> str:
    """Return a stable key for preserving the Plotly viewport.

    Parameters
    ----------
    network : networkx.DiGraph
        Live qBrain network.

    Returns
    -------
    str
        Representation of the topology that changes only with nodes or edges.
    """
    return repr((sorted(network.nodes), sorted(network.edges)))


def network_structure(network: nx.DiGraph) -> NetworkStructure:
    """Return the immutable information needed to draw a network.

    Parameters
    ----------
    network : networkx.DiGraph
        Live qBrain network.

    Returns
    -------
    tuple
        Sorted node IDs and classes followed by sorted directed edges.
    """
    nodes = tuple(
        sorted(
            (node, str(attributes.get("class", "")))
            for node, attributes in network.nodes(data=True)
        )
    )
    return nodes, tuple(sorted(network.edges))


@lru_cache(maxsize=8)
def base_figure(structure: NetworkStructure) -> go.Figure:
    """Draw and cache the static geometry for a network structure.

    Parameters
    ----------
    structure : tuple
        Immutable structure returned by :func:`network_structure`.

    Returns
    -------
    plotly.graph_objects.Figure
        Static architecture figure. Callers must copy it before mutation.
    """
    nodes, edges = structure
    network = nx.DiGraph()
    network.add_nodes_from((node, {"class": class_name}) for node, class_name in nodes)
    network.add_edges_from(edges)
    return draw(network)


def build_live_figure(network: nx.DiGraph) -> go.Figure:
    """Build a live figure while reusing its static graph geometry.

    Parameters
    ----------
    network : networkx.DiGraph
        Network containing the current qUnit outputs.

    Returns
    -------
    plotly.graph_objects.Figure
        Independent figure styled with the latest outputs.
    """
    figure = go.Figure(base_figure(network_structure(network)))
    return style_live_figure(figure, network)


def style_live_figure(figure: go.Figure, network: nx.DiGraph) -> go.Figure:
    """Apply compact live-signal styling to a qBrain figure.

    Parameters
    ----------
    figure : plotly.graph_objects.Figure
        Figure returned by :func:`qrobot_visualization.draw`.
    network : networkx.DiGraph
        Network containing current runtime outputs.

    Returns
    -------
    plotly.graph_objects.Figure
        The supplied figure with live labels, hover details, and signal styling.
    """
    for trace, (source, _) in zip(figure.data, network.edges):
        strength = signal_strength(network.nodes[source].get("output"))
        trace.update(mode="lines", text=None, opacity=0.25 + 0.75 * strength)
        trace.line.width = 1 + 3 * strength

    labels: list[str] = []
    hover: list[str] = []
    for node, attributes in network.nodes(data=True):
        raw = attributes.get("output")
        labels.append(node_label(node, attributes))
        hover.append(node_hover_text(node, raw))

    figure.data[-2].update(
        hoverinfo=None, hovertext=hover, hovertemplate="%{hovertext}<extra></extra>"
    )
    figure.data[-1].update(text=labels, textfont_size=11)
    figure.update_layout(
        uirevision=topology_key(network),
        font={"family": "Arial, sans-serif", "color": "#334155"},
    )
    return figure
