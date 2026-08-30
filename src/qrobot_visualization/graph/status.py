"""Redis status parsing for qBrain graphs."""

import json
from collections.abc import Mapping
from typing import Any

import networkx as nx

STATUS_ATTRIBUTES = (" class", " in_qunits", " output", " query", " state")


def is_status_key(key: str) -> bool:
    """Return whether a key describes a published unit attribute."""
    return any(attribute in key for attribute in STATUS_ATTRIBUTES)


def status_node_id(key: str) -> str:
    """Remove the published attribute suffix from a unit key."""
    for attribute in STATUS_ATTRIBUTES:
        key = key.replace(attribute, "")
    return key


def apply_node_status(graph: nx.DiGraph, node_id: str, key: str, value: Any) -> None:
    """Apply one published unit attribute to a graph node."""
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


def apply_input_status(graph: nx.DiGraph, node_id: str, key: str, value: Any) -> None:
    """Apply published input connections to a graph node."""
    if " in_qunits" not in key:
        return
    for input_id in json.loads(value).values():
        if input_id is not None:
            graph.add_edge(input_id, node_id)


def apply_status(graph: nx.DiGraph, status: Mapping[str, str]) -> None:
    """Overlay a decoded status mapping on a graph."""
    for key, value in status.items():
        if is_status_key(key):
            node_id = status_node_id(key)
            apply_node_status(graph, node_id, key, value)
            apply_input_status(graph, node_id, key, value)

    for source, target in graph.edges:
        output = graph.nodes[source].get("output")
        if output is not None:
            graph.edges[source, target]["output"] = output
