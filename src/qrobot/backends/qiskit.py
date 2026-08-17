"""Current Qiskit implementation of :class:`QuantumBackend`."""

from typing import Any

import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector

from .base import QuantumBackend


class QiskitBackend(QuantumBackend):
    """Simulate circuits using Qiskit's quantum-information API."""

    def create_circuit(self, qubits: int) -> QuantumCircuit:
        return QuantumCircuit(qubits)

    def sample_counts(self, circuit: Any, shots: int) -> dict[str, int]:
        counts = Statevector.from_instruction(circuit).sample_counts(shots)
        return {str(state): int(count) for state, count in counts.items()}

    def statevector(self, circuit: Any) -> np.ndarray:
        return np.asarray(Statevector.from_instruction(circuit).data)
