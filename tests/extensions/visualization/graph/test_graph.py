from networkx.readwrite.json_graph import node_link_data

from qrobot_visualization import build_network, graph


def test_graph():
    test_status = {
        "l0_unit_0 class": "SensorialUnit",
        "l0_unit_0 output": "0.438",
        "l1_unit0 class": "QUnit",
        "l1_unit0 in_qunits": '{"0": "l0_unit_0"}',
        "l1_unit0 output": "1.0",
        "l1_unit0 query": "[0.0]",
        "l1_unit0 state": "1",
        "l1_unit1 class": "QUnit",
        "l1_unit1 in_qunits": '{"0": "l0_unit_0"}',
        "l1_unit1 output": "1.0",
        "l1_unit1 query": "[0.8]",
        "l1_unit1 state": "0",
    }
    expected_json = {
        "directed": True,
        "multigraph": False,
        "graph": {},
        "nodes": [
            {"class": "SensorialUnit", "output": "0.438", "id": "l0_unit_0"},
            {
                "class": "QUnit",
                "output": "1.0",
                "query": [0.0],
                "state": "1",
                "id": "l1_unit0",
            },
            {
                "class": "QUnit",
                "output": "1.0",
                "query": [0.8],
                "state": "0",
                "id": "l1_unit1",
            },
        ],
        "edges": [
            {"output": "0.438", "source": "l0_unit_0", "target": "l1_unit0"},
            {"output": "0.438", "source": "l0_unit_0", "target": "l1_unit1"},
        ],
    }
    assert expected_json == node_link_data(graph(test_status))


def test_graph_allows_units_without_an_output_yet():
    """A partial Redis status remains renderable while workers are starting."""
    network = graph({"l1 class": "QUnit", "l1 in_qunits": '{"0": "l0"}'})

    assert set(network.nodes) == {"l0", "l1"}
    assert network.edges["l0", "l1"] == {}


def test_build_network_is_the_descriptive_public_api() -> None:
    """The preferred name has the same compatibility-preserving behaviour."""
    status = {"l0 class": "SensorialUnit"}

    assert node_link_data(build_network(status)) == node_link_data(graph(status))
