"""Redis status parsing for qBrain graphs."""

import json
from collections.abc import Mapping
from typing import Any

import networkx as nx
from qrobot_qunits.redis import RedisAttribute, parse_redis_key

STATUS_ATTRIBUTES = frozenset(
    {
        RedisAttribute.CLASS,
        RedisAttribute.IN_QUNITS,
        RedisAttribute.OUTPUT,
        RedisAttribute.QUERY,
        RedisAttribute.STATE,
    }
)


def is_status_key(key: str) -> bool:
    """Return whether a key describes a published unit attribute."""
    parsed = parse_redis_key(key)
    return parsed is not None and parsed.attribute in STATUS_ATTRIBUTES


def status_node_id(key: str) -> str:
    """Remove the published attribute suffix from a unit key."""
    parsed = parse_redis_key(key)
    return parsed.unit_id if parsed is not None and parsed.attribute in STATUS_ATTRIBUTES else key


def apply_node_status(graph: nx.DiGraph, node_id: str, key: str, value: Any) -> None:
    """Apply one published unit attribute to a graph node."""
    if node_id not in graph:
        graph.add_node(node_id)
    parsed = parse_redis_key(key)
    if parsed is None:
        return
    if parsed.attribute is RedisAttribute.CLASS:
        graph.nodes[node_id]["class"] = value
    elif parsed.attribute is RedisAttribute.OUTPUT:
        graph.nodes[node_id]["output"] = value
    elif parsed.attribute is RedisAttribute.STATE:
        graph.nodes[node_id]["state"] = value
    elif parsed.attribute is RedisAttribute.QUERY:
        try:
            graph.nodes[node_id]["query"] = json.loads(value)
        except TypeError, json.JSONDecodeError:
            pass


def apply_input_status(graph: nx.DiGraph, node_id: str, key: str, value: Any) -> None:
    """Apply published input connections to a graph node."""
    parsed = parse_redis_key(key)
    if parsed is None or parsed.attribute is not RedisAttribute.IN_QUNITS:
        return
    try:
        inputs = json.loads(value)
    except TypeError, json.JSONDecodeError:
        return
    if not isinstance(inputs, dict):
        return
    for input_id in inputs.values():
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
