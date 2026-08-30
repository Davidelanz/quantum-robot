"""Plotly rendering for quantum-robot network graphs."""

from typing import Any, cast

from matplotlib import colors, colormaps
import networkx as nx
import numpy as np
import plotly.graph_objects as go


def _hex_color(value: float) -> str:
    """Map a normalized value to a hexadecimal color from ``coolwarm``."""
    cmap: colors.Colormap = colormaps["coolwarm"]
    rgb_tuple = cmap(value)
    hex_color = colors.to_hex(rgb_tuple)
    return hex_color


def _positions(graph: nx.Graph) -> dict[str, np.ndarray]:
    """Calculate planar ``(x, y)`` positions for the graph nodes.

    Parameters
    ----------
    graph : networkx.Graph
        Graph whose nodes need positions.

    Returns
    -------
    dict[str, numpy.ndarray]
        Node positions keyed by node identifier.
    """
    return cast(dict[str, np.ndarray], nx.planar_layout(graph))


def _edge_trace(
    pos_1: np.ndarray,
    pos_2: np.ndarray,
    text: str,
    width: int,
    font_size: int,
    color: str,
) -> go.Scatter:
    """Create an edge between two nodes.

    Parameters
    ----------
    pos_1 : numpy.ndarray
        ``(x, y)`` position of the source node.
    pos_2 : numpy.ndarray
        ``(x, y)`` position of the destination node.
    text : str
        Annotation displayed on the edge.
    width : int
        Edge width in pixels.
    font_size : int
        Annotation font size in pixels.
    color : str
        Edge color as a hexadecimal string.

    Returns
    -------
    plotly.graph_objects.Scatter
        Scatter trace representing the edge.
    """
    x1, y1 = pos_1
    x2, y2 = pos_2
    mid_x = np.average([x1, x2])
    mid_y = np.average([y1, y2])
    return go.Scatter(
        x=[x1, mid_x, x2],
        y=[y1, mid_y, y2],
        text=[None, text, None],
        line=dict(width=width, color=color),
        textfont_size=font_size,
        textposition="top center",
        hoverinfo="none",
        mode="lines+text",
    )


def _edge_traces(
    graph: nx.Graph,
    positions: dict[str, np.ndarray],
    width: int,
    font_size: int,
) -> list[go.Scatter]:
    """For each edge, generate a trace and append it to the returned list."""
    edge_traces = []

    for edge in graph.edges():
        node_1, node_2 = edge

        edge_attributes: dict[str, Any] = graph.edges()[edge]
        output = edge_attributes.get("output", None)
        output_str = f"{output}<br>" if output else ""

        color = _hex_color(float(output)) if output else "lightgray"

        trace = _edge_trace(
            positions[node_1],
            positions[node_2],
            text=output_str,
            width=width,
            font_size=font_size,
            color=color,
        )
        edge_traces.append(trace)

    return edge_traces


def _node_trace(
    graph: nx.Graph,
    positions: dict[str, np.ndarray],
    size: int,
    font_size: int,
) -> go.Scatter:
    """Generate the node trace."""
    node_trace = go.Scatter(
        x=[],
        y=[],
        text=[],
        textposition="top center",
        textfont_size=font_size,
        mode="markers+text",
        hoverinfo="none",
        marker=dict(color=[], size=[], line=None),
    )

    # Plotly stores all node coordinates and labels in one scatter trace.
    for node in graph.nodes():
        node_attributes: dict[str, Any] = graph.nodes()[node]

        node_class = node_attributes.get("class", None)
        query = node_attributes.get("query", None)
        state = node_attributes.get("state", None)
        output = node_attributes.get("output", None)

        class_str = f"<b>{node_class}</b><br>" if node_class else ""
        id_str = f"<i>{node}</i><br>"
        query_str = f"Query: {query}<br>" if state else ""
        state_str = f"State: |{state}⟩<br>" if state else ""
        output_str = f"Output: {output}<br>" if output else ""

        color = _hex_color(float(output)) if output else "lightgray"
        text = class_str + id_str + query_str + state_str + output_str

        x, y = positions[node]
        node_trace["x"] += tuple([x])
        node_trace["y"] += tuple([y])
        node_trace["marker"]["color"] += tuple([color])
        node_trace["marker"]["size"] += tuple([size])
        node_trace["text"] += tuple([text])

    return node_trace


def _layout() -> go.Layout:
    """Return the layout used by generated figures."""
    return go.Layout(
        paper_bgcolor="rgba(0,0,0,0)",  # transparent background
        plot_bgcolor="rgba(0,0,0,0)",  # transparent 2nd background
        showlegend=False,
        xaxis={
            "showticklabels": False,
            # No gridlines:
            "showgrid": False,
            "zeroline": False,
        },
        yaxis={
            "showticklabels": False,
            # No gridlines:
            "showgrid": False,
            "zeroline": False,
        },
    )


def draw(
    graph: nx.Graph,
) -> go.Figure:
    """Visualize a directed graph containing all the running units as connected nodes.

    Parameters
    ----------
    graph : networkx.Graph
        Directed qUnit network to render.

    Returns
    -------
    plotly.graph_objects.Figure
        Generated figure. Call ``figure.show()`` from an interactive application
        to display it.
    """
    # Create figure
    fig = go.Figure(layout=_layout())
    # Get the positions
    positions = _positions(graph)
    # Add all edge traces
    for trace in _edge_traces(graph, positions, width=2, font_size=12):
        fig.add_trace(trace)
    # Add node trace
    fig.add_trace(_node_trace(graph, positions, size=25, font_size=12))
    # Keep labels visible when they extend past the axis bounds.
    fig.update_traces(cliponaxis=False)
    return fig
