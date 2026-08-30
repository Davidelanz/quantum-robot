from dataclasses import dataclass, field

from qrobot_visualization.graph.architecture import (
    build_architecture,
    iter_units,
    unit_attributes,
    unit_group,
)


@dataclass
class SensorialUnit:
    id: str = "sensor-id"
    name: str = "sensor"
    sampling_period: float = 0.1
    default_input: float = 0.0


@dataclass
class AngularModel:
    n: int = 1
    tau: int = 10


class ZeroBurst:
    pass


@dataclass
class QUnit:
    id: str = "processor-id"
    name: str = "processor"
    sampling_period: float = 0.1
    in_qunits: dict[int, str] = field(default_factory=lambda: {0: "sensor-id"})
    query: list[float] = field(default_factory=lambda: [1.0])
    model: AngularModel = field(default_factory=AngularModel)
    burst: ZeroBurst = field(default_factory=ZeroBurst)


@dataclass
class ActuatorUnit:
    id: str = "actuator-id"
    name: str = "actuator"
    sampling_period: float = 0.1
    in_qunits: dict[int, str] = field(default_factory=lambda: {0: "processor-id"})
    threshold: float = 0.5
    default_input: float = 0.0


def configured_units() -> tuple[SensorialUnit, QUnit, ActuatorUnit]:
    sensor = SensorialUnit()
    processor = QUnit()
    actuator = ActuatorUnit()
    return sensor, processor, actuator


def test_iter_units_flattens_qbrain_containers() -> None:
    sensor, processor, actuator = configured_units()

    assert list(iter_units(({"sensor": sensor}, [processor], actuator))) == [
        sensor,
        processor,
        actuator,
    ]


def test_unit_group_uses_unit_type() -> None:
    sensor, processor, actuator = configured_units()

    assert [unit_group(unit) for unit in (sensor, processor, actuator)] == [
        "sensorial",
        "qbrain",
        "actuator",
    ]


def test_unit_attributes_summarize_qbrain_configuration() -> None:
    _, processor, _ = configured_units()

    attributes = unit_attributes(processor, processor.id)

    assert attributes["model"] == "AngularModel (n: 1, τ: 10)"
    assert attributes["burst"] == "ZeroBurst"
    assert attributes["sampling_period"] == 0.1


def test_build_architecture_uses_configured_wiring() -> None:
    sensor, processor, actuator = configured_units()

    graph = build_architecture((sensor, processor, actuator))

    assert list(graph.edges) == [(sensor.id, processor.id), (processor.id, actuator.id)]
    assert graph.nodes[processor.id]["query"] == [1.0]
