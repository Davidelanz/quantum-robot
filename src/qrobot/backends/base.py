"""Stable interface between qRobot models and quantum SDKs."""

from abc import ABC, abstractmethod
from typing import Any

import numpy as np


class QuantumBackend(ABC):
    """Create and simulate the circuits used by qRobot models."""

    @abstractmethod
    def create_circuit(self, qubits: int) -> Any:
        """Return a circuit with ``qubits`` quantum bits."""

    @abstractmethod
    def sample_counts(self, circuit: Any, shots: int) -> dict[str, int]:
        """Sample computational-basis counts without mutating ``circuit``."""

    @abstractmethod
    def statevector(self, circuit: Any) -> np.ndarray:
        """Return the circuit's final statevector."""
