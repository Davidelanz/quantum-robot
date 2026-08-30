"""Plotly traces for qBrain nodes and edges."""

from typing import Any

import networkx as nx
import numpy as np
import plotly.graph_objects as go

from .colors import EDGE_COLORS, NODE_COLORS
from .layout import node_role

NODE_EDGE_OFFSET = 0.2


def edge_coordinates(
    source_position: np.ndarray,
    target_position: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """Return a curved path clipped to the source and target node edges."""
    source_x, source_y = source_position
    target_x, target_y = target_position
    start_x = source_x + NODE_EDGE_OFFSET
    end_x = target_x - NODE_EDGE_OFFSET
    progress = np.linspace(0.0, 1.0, 25)
    control_x = (start_x + end_x) / 2
    x_values = (
        (1 - progress) ** 3 * start_x
        + 3 * (1 - progress) ** 2 * progress * control_x
        + 3 * (1 - progress) * progress**2 * control_x
        + progress**3 * end_x
    )
    y_values = (
        (1 - progress) ** 3 * source_y
        + 3 * (1 - progress) ** 2 * progress * source_y
        + 3 * (1 - progress) * progress**2 * target_y
        + progress**3 * target_y
    )
    return x_values, y_values


def edge_trace(
    source_position: np.ndarray,
    target_position: np.ndarray,
    text: str,
    width: int,
    font_size: int,
    color: str,
) -> go.Scatter:
    """Create one smoothly routed edge trace."""
    x_values, y_values = edge_coordinates(source_position, target_position)
    return go.Scatter(
        x=x_values[:-1],
        y=y_values[:-1],
        text=[text if index == len(x_values) // 2 else None for index in range(len(x_values) - 1)],
        line={"width": width, "color": color},
        textfont_size=font_size,
        textposition="top center",
        hoverinfo="none",
        mode="lines+text",
    )


def edge_traces(
    graph: nx.Graph,
    positions: dict[str, np.ndarray],
    width: int,
    font_size: int,
) -> list[go.Scatter]:
    """Create traces for every graph edge."""
    traces = []
    for source, target in graph.edges:
        attributes: dict[str, Any] = graph.edges[source, target]
        output = attributes.get("output")
        traces.append(
            edge_trace(
                positions[source],
                positions[target],
                text=f"{output}<br>" if output is not None else "",
                width=width,
                font_size=font_size,
                color=EDGE_COLORS[node_role(graph, target)],
            )
        )
    return traces


def add_edge_arrows(
    figure: go.Figure,
    graph: nx.Graph,
    positions: dict[str, np.ndarray],
) -> None:
    """Add a directional arrowhead at the target of every edge."""
    for source, target in graph.edges:
        x_values, y_values = edge_coordinates(positions[source], positions[target])
        figure.add_annotation(
            x=float(x_values[-1]),
            y=float(y_values[-1]),
            ax=float(x_values[-2]),
            ay=float(y_values[-2]),
            xref="x",
            yref="y",
            axref="x",
            ayref="y",
            text="",
            showarrow=True,
            arrowhead=2,
            arrowsize=0.85,
            arrowwidth=2,
            arrowcolor=EDGE_COLORS[node_role(graph, target)],
        )


def node_text(node: str, attributes: dict[str, Any]) -> str:
    """Format a compact visible node label."""
    parts = [f"<b>{attributes.get('name', node)}</b>"]
    if attributes.get("model") is not None:
        parts.extend(
            [
                str(attributes["model"]),
                str(attributes["burst"]),
                f"query: {attributes['query']}",
            ]
        )
    elif attributes.get("threshold") is not None:
        parts.extend([f"threshold: {attributes['threshold']}"])
    if attributes.get("sampling_period") is not None:
        parts.append(f"Tₛ: {attributes['sampling_period']}")
    return "<br>".join(parts)


def node_trace(
    graph: nx.Graph,
    positions: dict[str, np.ndarray],
    size: int,
) -> go.Scatter:
    """Create the marker trace for every graph node."""
    trace = go.Scatter(
        x=[],
        y=[],
        mode="markers",
        hoverinfo="none",
        marker={"color": [], "size": [], "line": None},
    )
    for node in graph.nodes:
        x, y = positions[node]
        trace["x"] += (x,)
        trace["y"] += (y,)
        trace["marker"]["color"] += (NODE_COLORS[node_role(graph, node)],)
        trace["marker"]["size"] += (size,)
    return trace


def node_text_trace(
    graph: nx.Graph,
    positions: dict[str, np.ndarray],
    font_size: int,
    vertical_offset: float,
) -> go.Scatter:
    """Create node labels below their markers."""
    return go.Scatter(
        x=[positions[node][0] for node in graph.nodes],
        y=[positions[node][1] - vertical_offset for node in graph.nodes],
        text=[node_text(node, graph.nodes[node]) for node in graph.nodes],
        textposition="top center",
        textfont_size=font_size,
        mode="text",
        hoverinfo="none",
    )
