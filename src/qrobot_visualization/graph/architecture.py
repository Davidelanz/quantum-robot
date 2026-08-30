"""Static qBrain architecture construction."""

from collections.abc import Iterable, Mapping
from typing import Any

import networkx as nx


def iter_units(source: object) -> Iterable[Any]:
    """Yield units from nested mappings and collections."""
    if isinstance(source, Mapping):
        for unit in source.values():
            yield from iter_units(unit)
    elif isinstance(source, (list, tuple, set)):
        for unit in source:
            yield from iter_units(unit)
    else:
        yield source


def unit_group(unit: object) -> str:
    """Return the architecture group for a configured unit."""
    class_name = unit.__class__.__name__
    if class_name == "SensorialUnit":
        return "sensorial"
    if class_name == "ActuatorUnit":
        return "actuator"
    return "qbrain"


def unit_attributes(unit: object, node_id: str) -> dict[str, Any]:
    """Return display attributes for one configured unit."""
    attributes: dict[str, Any] = {
        "class": unit.__class__.__name__,
        "name": getattr(unit, "name", node_id),
        "group": unit_group(unit),
    }
    sampling_period = getattr(unit, "sampling_period", None)
    if sampling_period is not None:
        attributes["sampling_period"] = sampling_period

    model = getattr(unit, "model", None)
    if model is not None:
        model_name = model.__class__.__name__
        model_n = getattr(model, "n", None)
        model_tau = getattr(model, "tau", None)
        attributes["model"] = (
            f"{model_name} (n: {model_n}, τ: {model_tau})"
            if model_n is not None and model_tau is not None
            else model_name
        )
    burst = getattr(unit, "burst", None)
    if burst is not None:
        attributes["burst"] = burst.__class__.__name__
    query = getattr(unit, "query", None)
    if query is not None:
        attributes["query"] = list(query)
    threshold = getattr(unit, "threshold", None)
    if threshold is not None:
        attributes["threshold"] = threshold
    default_input = getattr(unit, "default_input", None)
    if default_input is not None:
        attributes["default_input"] = default_input
    return attributes


def build_architecture(source: object) -> nx.DiGraph:
    """Build graph topology from configured qUnit-like objects."""
    graph = nx.DiGraph()
    units: list[Any] = list(iter_units(source))

    for unit in units:
        node_id = getattr(unit, "id", None)
        if not isinstance(node_id, str):
            raise TypeError("architecture sources must contain qUnit-like objects with an id")
        graph.add_node(node_id, **unit_attributes(unit, node_id))

    for unit in units:
        incoming = getattr(unit, "in_qunits", {})
        inputs = incoming.values() if isinstance(incoming, Mapping) else incoming
        for input_id in inputs:
            if input_id is not None:
                graph.add_edge(input_id, unit.id)

    return graph
