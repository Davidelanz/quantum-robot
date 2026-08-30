"""Layered qBrain graph layout."""

import networkx as nx
import numpy as np
import plotly.graph_objects as go


def node_group(graph: nx.Graph, node: str) -> str:
    """Classify a graph node as sensorial, qBrain, or actuator."""
    attributes = graph.nodes[node]
    if attributes.get("group"):
        return str(attributes["group"])
    if attributes.get("class") == "SensorialUnit":
        return "sensorial"
    if attributes.get("class") == "ActuatorUnit":
        return "actuator"
    return "qbrain"


def node_role(graph: nx.Graph, node: str) -> str:
    """Return the visual role of a node in the architecture."""
    group = node_group(graph, node)
    if group != "qbrain":
        return group
    predecessors = graph.predecessors(node) if graph.is_directed() else graph.neighbors(node)
    if any(node_group(graph, predecessor) == "sensorial" for predecessor in predecessors):
        return "perceptual"
    return "cognitive"


def node_generations(graph: nx.Graph) -> dict[str, int]:
    """Return each node's longest-path generation."""
    generations: dict[str, int] = {}
    nodes = nx.topological_sort(graph) if nx.is_directed_acyclic_graph(graph) else graph
    for node in nodes:
        predecessors = list(graph.predecessors(node)) if graph.is_directed() else []
        generations[node] = max(
            (generations.get(predecessor, 0) + 1 for predecessor in predecessors),
            default=0,
        )
    return generations


def architecture_columns(graph: nx.Graph) -> list[list[str]]:
    """Return ordered node columns from sensors through actuators."""
    groups = {node: node_group(graph, node) for node in graph.nodes}
    generations = node_generations(graph)
    qbrain = [node for node in graph if groups[node] == "qbrain"]
    qbrain_layers = sorted({generations.get(node, 1) for node in qbrain})
    columns = [[node for node in graph if groups[node] == "sensorial"]]
    columns.extend(
        [node for node in qbrain if generations[node] == layer] for layer in qbrain_layers
    )
    columns.append([node for node in graph if groups[node] == "actuator"])
    return columns


def node_positions(graph: nx.Graph) -> dict[str, np.ndarray]:
    """Place nodes in spacious left-to-right architecture layers."""
    columns = architecture_columns(graph)
    horizontal_spacing = 1.1
    vertical_spacing = 2.1

    positions: dict[str, np.ndarray] = {}
    for column_index, nodes in enumerate(columns):
        x = column_index * horizontal_spacing
        for index, node in enumerate(nodes):
            y = ((len(nodes) - 1) / 2 - index) * vertical_spacing
            positions[node] = np.array([x, y], dtype=float)
    return positions


def figure_height(graph: nx.Graph) -> int:
    """Return a bounded initial height for an interactive figure."""
    columns = architecture_columns(graph)
    return min(
        760,
        max(480, 90 * max((len(column) for column in columns), default=1) + 120),
    )


def figure_layout(graph: nx.Graph) -> go.Layout:
    """Return a canvas scaled for the supplied qBrain graph."""
    axis = {"showticklabels": False, "showgrid": False, "zeroline": False}
    return go.Layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
        autosize=True,
        margin={"l": 40, "r": 40, "t": 55, "b": 30},
        height=figure_height(graph),
        xaxis=axis,
        yaxis=axis,
    )


def add_group_blocks(
    figure: go.Figure,
    graph: nx.Graph,
    positions: dict[str, np.ndarray],
) -> None:
    """Add the sensorial, qBrain, and actuator background blocks."""
    if not positions:
        return
    styles = {
        "sensorial": ("Sensorial", "rgba(91, 120, 230, 0.14)"),
        "qbrain": ("Q-Brain", "rgba(246, 194, 62, 0.16)"),
        "actuator": ("Actuators", "rgba(93, 174, 81, 0.15)"),
    }
    y_values = [float(position[1]) for position in positions.values()]
    y_min, y_max = min(y_values) - 0.4, max(y_values) + 1.2
    for group, (label, color) in styles.items():
        x_values = [float(positions[node][0]) for node in graph if node_group(graph, node) == group]
        if not x_values:
            continue
        x_min, x_max = min(x_values), max(x_values)
        figure.add_shape(
            type="rect",
            x0=x_min - 0.4,
            x1=x_max + 0.4,
            y0=y_min,
            y1=y_max,
            fillcolor=color,
            line={"width": 0},
            layer="below",
        )
        figure.add_annotation(
            x=(x_min + x_max) / 2,
            y=y_max,
            text=f"<b>{label}</b>",
            showarrow=False,
            yshift=14,
        )
