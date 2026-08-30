"""NetworkX graph construction from qUnit Redis status data."""

import json
from collections.abc import Mapping
from typing import Any

import networkx as nx

ATTRIBUTES = [
    " class",
    " in_qunits",
    " output",
    " query",
    " state",
]


def _is_id(candidate_key: str) -> bool:
    """Return whether a Redis key belongs to a published unit attribute."""
    return any(attribute in candidate_key for attribute in ATTRIBUTES)


def _get_id(key: str) -> str:
    """Remove the attribute suffix from a unit's Redis key."""
    for attr in ATTRIBUTES:
        key = key.replace(attr, "")
    return key


def _write_node(graph: nx.Graph, node_id: str, key: str, value: Any) -> None:
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


def _write_edge(graph: nx.Graph, node_id: str, key: str, value: Any) -> None:
    """Link units in the network by adding the respective edges."""
    if " in_qunits" in key:
        in_qunits = json.loads(value)
        for _, in_qunit in in_qunits.items():
            if (in_qunit, node_id) not in graph.edges():
                graph.add_edge(in_qunit, node_id)


def build_network(status_dict: Mapping[str, str]) -> nx.DiGraph:
    """Build a directed unit network from a Redis status snapshot.

    Parameters
    ----------
    status_dict : collections.abc.Mapping[str, str]
        Decoded Redis keys and values.

    Returns
    -------
    networkx.DiGraph
        Units as nodes and input couplings as edges.
    """
    graph = nx.DiGraph()

    for key, value in status_dict.items():
        if _is_id(key):
            node_id = _get_id(key)
            _write_node(graph, node_id, key, value)
            _write_edge(graph, node_id, key, value)

    for source, target in graph.edges():
        output = graph.nodes[source].get("output")
        if output is not None:
            graph.edges[source, target]["output"] = output

    return graph


def graph(status_dict: Mapping[str, str]) -> nx.DiGraph:
    """Build a network graph from Redis status data.

    Parameters
    ----------
    status_dict : collections.abc.Mapping[str, str]
        Decoded Redis keys and values.

    Returns
    -------
    networkx.DiGraph
        Units as nodes and input couplings as edges.

    Notes
    -----
    Deprecated alias for :func:`build_network`. It remains available so
    existing applications can move to the less ambiguous public name.
    """
    return build_network(status_dict)
