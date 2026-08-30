from qrobot_visualization import build_network
from qrobot_visualization.graph.build import is_status_mapping


def test_is_status_mapping_distinguishes_unit_collections() -> None:
    assert is_status_mapping({"sensor class": "SensorialUnit"})
    assert not is_status_mapping({"sensor": object()})


def test_build_network_accepts_status() -> None:
    network = build_network(
        {
            "sensor class": "SensorialUnit",
            "processor class": "QUnit",
            "processor in_qunits": '{"0": "sensor"}',
        }
    )

    assert set(network) == {"sensor", "processor"}
    assert list(network.edges) == [("sensor", "processor")]


def test_build_network_keeps_status_dict_keyword_compatibility() -> None:
    network = build_network(status_dict={"sensor class": "SensorialUnit"})

    assert set(network) == {"sensor"}
