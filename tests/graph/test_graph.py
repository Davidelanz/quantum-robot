from networkx.readwrite.json_graph import node_link_data

from qrobot import graph


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
        "links": [
            {"output": "0.438", "source": "l0_unit_0", "target": "l1_unit0"},
            {"output": "0.438", "source": "l0_unit_0", "target": "l1_unit1"},
        ],
    }
    assert expected_json == node_link_data(graph(test_status))
