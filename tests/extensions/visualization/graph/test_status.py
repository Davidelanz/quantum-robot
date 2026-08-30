import networkx as nx

from qrobot_visualization.graph.status import apply_status, is_status_key, status_node_id


def test_is_status_key_recognizes_attributes() -> None:
    assert is_status_key("sensor class")
    assert not is_status_key("sensor")


def test_status_node_id_removes_attribute_suffix() -> None:
    assert status_node_id("sensor in_qunits") == "sensor"


def test_apply_status_adds_nodes_edges_and_live_outputs() -> None:
    graph = nx.DiGraph()

    apply_status(
        graph,
        {
            "sensor class": "SensorialUnit",
            "sensor output": "0.0",
            "processor class": "QUnit",
            "processor in_qunits": '{"0": "sensor"}',
            "processor query": "[1.0]",
        },
    )

    assert graph.nodes["processor"]["query"] == [1.0]
    assert graph.edges["sensor", "processor"]["output"] == "0.0"
