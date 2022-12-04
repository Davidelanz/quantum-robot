from typing import Dict, List, Optional, Tuple

import matplotlib as mpl
import networkx as nx
import numpy as np
import plotly.graph_objects as go


def _hex_color(value: float) -> str:
    """Convert a value in the interval [0.0, 1.0] to the HEX color given the Colormap."""
    cmap: mpl.colors.Colormap = mpl.colormaps["coolwarm"]
    rgb_tuple = cmap(value)
    hex_color = mpl.colors.to_hex(rgb_tuple)
    return hex_color


def _positions(graph: nx.Graph) -> Dict[str, np.ndarray]:
    """Get positions for a input graph.
    Positions are provided as np.ndarray(x, y).

    Args:
        graph (nx.Graph): The input graph

    Returns:
        dict: A dictionary of positions keyed by node
    """
    return nx.planar_layout(graph)


def _edge_trace(
    pos_1: np.ndarray,
    pos_2: np.ndarray,
    text,
    width: int,
    font_size: int,
    color: Tuple[float, float, float, float],
) -> go.Scatter:
    """Create an edge between two nodes.

    Args:
        node_1 (np.ndarray): Position (x,y) of the first node.
        node_2 (np.ndarray(x, y): Position (x,y) of the second node.
        text (str): Annotation text for the edge.
        width (int): Edge width.
        font_size (int): Annotation text font size.
        color (str): Edge color (HEX string format).

    Returns:
        go.Scatter: Edge scatter trace
    """
    x1, y1 = pos_1
    x2, y2 = pos_2
    mid_x = np.average([x1, x2])
    mid_y = np.average([y1, y2])
    # TODO: evaluate https://github.com/redransil/plotly-dirgraph/ to add the arrow
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
    positions: Dict[str, np.ndarray],
    width: int,
    font_size: int,
) -> List[go.Scatter]:
    """For each edge, generate a trace and append it to the returned list."""
    edge_traces = []

    for edge in graph.edges():
        node_1, node_2 = edge

        edge_attributes: dict = graph.edges()[edge]
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
    positions: Dict[str, np.ndarray],
    size: int,
    font_size: int,
) -> List[go.Scatter]:
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

    # For each node in G, get the position and size and add to the node_trace
    for node in graph.nodes():
        node_attributes: dict = graph.nodes()[node]

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
    """Custom layout for the generated figure."""
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
    show: bool = True,
    return_figure: bool = False,
    static_plot: bool = True,
) -> Optional[go.Figure]:
    """Visualize a directed graph containing all the running units as connected nodes.

    Args:
        graph (nx.Graph): The directed graph.
        show (bool, optional): Whether to show the generated plotly Figure.
            Defaults to True.
        return_figure (bool, optional): Whether to return the generated plotly Figure.
            Defaults to False.
        static_plot (bool, optional): Whether to have a static or interactive
            plotly Figure. Defaults to True.

    Returns:
        go.Figure: The generated plotly Figure (if ``return_figure`` is ``True``).
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
    # Avoid text label clipping after adding al the traces
    fig.update_traces(cliponaxis=False)
    # Show figure
    if show:
        config = {"staticPlot": static_plot}
        fig.show(config=config)
    if return_figure:
        return fig
