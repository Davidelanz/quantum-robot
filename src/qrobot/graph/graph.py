import json
from typing import Any

import networkx as nx

ATTRIBUTES = [
    " class",
    " in_qunits",
    " output",
    " query",
    " state",
]


def _is_id(candidate_key: str):
    """Check if a candidate Redis key contains a unit id."""
    return any([x in candidate_key for x in ATTRIBUTES])


def _get_id(key: str):
    """Get unit id from a Redis key."""
    for attr in ATTRIBUTES:
        key = key.replace(attr, "")
    return key


def _write_node(graph: nx.Graph, node_id: str, key: str, value: Any):
    """Write unit attributes to the corresponding graph node."""
    if node_id not in graph:
        graph.add_node(node_id)
    if " class" in key:
        graph.nodes[node_id]["class"] = value
    elif " output" in key:
        graph.nodes[node_id]["output"] = value
    elif " state" in key:
        graph.nodes[node_id]["state"] = value
    elif " query" in key:
        graph.nodes[node_id]["query"] = json.loads(value)


def _write_edge(graph: nx.Graph, node_id: str, key: str, value: Any):
    """Link units in the network by adding the respective edges."""
    if " in_qunits" in key:
        in_qunits = json.loads(value)
        for _, in_qunit in in_qunits.items():
            if (in_qunit, node_id) not in graph.edges():
                graph.add_edge(in_qunit, node_id)


def graph(status_dict: dict) -> nx.DiGraph:
    """Given the Redis status dictionary, generate a `networkx` directed graph
    containing all the units connected as nodes.

    Args:
        status_dict (dict): The Redis status dictionary.

    Returns:
        networkx.DiGraph: The `networkx` directed graph
    """
    graph = nx.DiGraph()

    for key, value in status_dict.items():
        if _is_id(key):
            node_id = _get_id(key)
            _write_node(graph, node_id, key, value)
            _write_edge(graph, node_id, key, value)

    for edge in graph.edges():
        output = graph.nodes[edge[0]]["output"]
        graph.edges[edge]["output"] = output

    return graph
