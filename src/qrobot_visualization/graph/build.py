"""Public qBrain graph builders."""

from collections.abc import Mapping
from typing import Any, cast

import networkx as nx

from .architecture import build_architecture
from .status import apply_status, is_status_key


def is_status_mapping(source: Mapping[Any, Any]) -> bool:
    """Return whether a mapping contains published status keys."""
    return any(isinstance(key, str) and is_status_key(key) for key in source)


def build_network(
    source: object | None = None,
    status_dict: Mapping[str, str] | None = None,
) -> nx.DiGraph:
    """Build a directed qBrain graph from configured units or live status.

    Configured units describe the architecture without needing to be running.
    A status mapping can build the network from recorded values or add runtime
    values to an architecture built from configured units.

    Parameters
    ----------
    source : object, optional
        Unit, nested collection of units, or mapping of published unit
        attributes. Unit inputs determine the edges between nodes.
    status_dict : collections.abc.Mapping[str, str], optional
        Published unit attributes to add to the configured architecture. When
        ``source`` is omitted, this mapping defines the complete network.

    Returns
    -------
    networkx.DiGraph
        Directed network containing units as nodes and input couplings as
        edges.

    Examples
    --------
    Build a network from published unit attributes:

    >>> from qrobot_visualization import build_network
    >>> status = {
    ...     "sensor class": "SensorialUnit",
    ...     "processor class": "QUnit",
    ...     "processor in_qunits": '{"0": "sensor"}',
    ... }
    >>> network = build_network(status)
    >>> list(network.edges)
    [('sensor', 'processor')]
    """
    if source is None:
        source = status_dict if status_dict is not None else {}
        status_dict = None

    if isinstance(source, Mapping) and (is_status_mapping(source) or not source):
        graph = nx.DiGraph()
        apply_status(graph, cast(Mapping[str, str], source))
    else:
        graph = build_architecture(source)
        if status_dict is not None:
            apply_status(graph, status_dict)
    return graph
