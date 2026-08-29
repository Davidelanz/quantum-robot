import numpy as np

from qrobot.backends import QuantumBackend
from qrobot.models import AngularModel


class FakeCircuit:
    def __init__(self, qubits: int) -> None:
        self.qubits = qubits
        self.rotations: list[tuple[float, int]] = []

    def ry(self, angle: float, qubit: int) -> None:
        self.rotations.append((angle, qubit))


class FakeBackend(QuantumBackend):
    def create_circuit(self, qubits: int) -> FakeCircuit:
        return FakeCircuit(qubits)

    def sample_counts(self, circuit: FakeCircuit, shots: int) -> dict[str, int]:
        return {"1": shots}

    def statevector(self, circuit: FakeCircuit) -> np.ndarray:
        return np.array([0.0, 1.0])


def test_model_uses_backend_interface() -> None:
    backend = FakeBackend()
    model = AngularModel(n=1, tau=1, backend=backend)

    model.encode(1.0, dim=0)

    assert model.measure(shots=3) == {"1": 3}
    assert np.array_equal(model.get_statevector(), np.array([0.0, 1.0]))
    assert np.array_equal(model.get_density_matrix(), np.array([[0.0, 0.0], [0.0, 1.0]]))
    assert model.circ.rotations
    assert dict(model) == {"model": "AngularModel", "n": 1, "tau": 1}
    assert repr(model) == "[model: AngularModel, n: 1, tau: 1]"
