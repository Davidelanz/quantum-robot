"""qBrain figure rendering."""

import networkx as nx
import plotly.graph_objects as go

from .layout import add_group_blocks, figure_layout, node_positions
from .traces import add_edge_arrows, edge_traces, node_text_trace, node_trace


def draw(graph: nx.Graph) -> go.Figure:
    """Render a qBrain network as an interactive Plotly figure.

    Arrange sensorial units, qBrain layers, and actuator units from left to
    right. Node and edge colors identify their architectural roles, while
    directed arrows show the configured flow of information.

    Parameters
    ----------
    graph : networkx.Graph
        Network whose nodes contain the attributes produced by
        :func:`qrobot_visualization.build_network`.

    Returns
    -------
    plotly.graph_objects.Figure
        Interactive architecture figure that can be displayed directly or
        embedded with Plotly's ``to_html`` method.

    Examples
    --------
    >>> from qrobot_visualization import build_network, draw
    >>> network = build_network(status_dict={"sensor class": "SensorialUnit"})
    >>> figure = draw(network)
    """
    figure = go.Figure(layout=figure_layout(graph))
    positions = node_positions(graph)
    add_group_blocks(figure, graph, positions)
    for trace in edge_traces(graph, positions, width=2, font_size=12):
        figure.add_trace(trace)
    add_edge_arrows(figure, graph, positions)
    figure.add_trace(node_trace(graph, positions, size=30))
    figure.add_trace(node_text_trace(graph, positions, font_size=9, vertical_offset=0.2))
    figure.update_traces(cliponaxis=False)
    return figure
