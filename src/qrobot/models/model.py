from abc import ABC, abstractmethod
from typing import Dict

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import qiskit
import seaborn as sns
from qiskit.providers import Backend, BaseJob
from qiskit.quantum_info import Operator, Statevector
from qiskit.result import Result


class Model(ABC):
    """``Model`` is an abstract class which embeds the general features
    needed in a model for QL perception.


    Parameters
    ----------
    n : int
        Model's dimension (must be greater than 0)
    tau : int
        Number of samples of the temporal window (must be greater than 0)

    Attributes
    ----------
    n : int
        Model's dimension.
    tau : int
        Number of samples of the temporal window.
    circ : qiskit.QuantumCircuit
        Quantum circuit which implements the model.
    """

    def __init__(self, n, tau) -> None:  # pylint: disable=invalid-name
        """Initialize the class"""

        # Check the argument n
        if isinstance(n, int):
            if n > 0:
                self.n = n  # pylint: disable=invalid-name
            else:
                raise ValueError("n must be greater than 0!")
        else:
            raise TypeError("n must be an integer!")

        # Check the argument tau
        if isinstance(tau, int):
            if tau > 0:
                self.tau = tau
            else:
                raise ValueError("tau must be greater than 0!")
        else:
            raise TypeError("tau must be an integer!")

        # Initialize the circuit
        self.circ = qiskit.QuantumCircuit(n, n)

    def __iter__(self):
        yield "model", self.__class__.__name__
        yield "n", self.n
        yield "tau", self.tau

    def __repr__(self) -> str:
        out_str = "["
        for key, value in dict(self).items():
            out_str += f"{key}: {value}, "
        return out_str[:-2] + "]"

    def _dim_index_check(self, dim) -> int:
        """This method ensures that a dimension index `dim`
        is an integer between 0 and `n-1`, where `n` is the dimension
        of the model.

        Raises
        ---------
        TypeError
            `dim` is not an integer `int`
        ValueError
            `dim` is not greater than 0
        IndexError
            `dim` is greater than the model dimension `n`

        Returns
        --------
        int
            The dimension index `dim`
        """
        if not isinstance(dim, int):
            raise TypeError("dim must be an integer!")
        if dim < 0:
            raise ValueError("dim must be greater or equal to 0!")
        if dim >= self.n:
            raise IndexError(f"dim must be less than {self.n}!")
        return dim

    @staticmethod
    def _scalar_input_check(scalar_input) -> float:
        """This method ensures that a `scalar_input` for the model
        is an integer or a float between 0 and 1 (inclusive).

        Raises
        ---------
        TypeError:
            `scalar_input` is nor a `int` or a `float`
        ValueError
            `scalar_input` is not between 0 and 1 inclusive

        Returns
        --------
        float
            The `scalar_input`
        """
        if not isinstance(scalar_input, (float, int)):
            raise TypeError(
                f"input must be an scalar number, not a {type(scalar_input)}!"
            )
        if scalar_input > 1 or scalar_input < 0:
            raise ValueError("scalar_input must be between 0 and 1 inclusive!")
        return float(scalar_input)

    def _target_vector_check(self, target_vector) -> list:
        """This method ensures that a `target_vector` for the model
        is an `n`-dimensional vector (where `n` is the model's dimension).

        Raises
        ---------
        TypeError
            `target_vector` elements are not all integers or floats
        ValueError
            `target_vector` dimension does not match model's dimension `n`
        ValueError
            `target_vector` elements are not not all between 0 and 1 inclusive

        Returns
        ----------
        list
            The `target_vector`
        """
        # If target_vector is a single number,
        # convert it in a single-element vector
        if isinstance(target_vector, (float, int)):
            target_vector = [target_vector]
        # Dimensionality check on the vector
        if len(target_vector) is not self.n:
            raise ValueError(
                f"target_vector must be a {self.n}\
                             -dimensional vector!"
            )
        for element in target_vector:
            if not isinstance(element, (float, int)):
                raise TypeError(
                    "target_vector elements must be all integers or floats!"
                )
            if element > 1 or element < 0:
                raise ValueError(
                    "target_vector elements must be all between \
                    0 and 1 inclusive!"
                )
        return target_vector

    def clear(self) -> None:
        """Re-initialize the model with an empty circuit."""
        self.circ = qiskit.QuantumCircuit(self.n, self.n)

    @abstractmethod
    def encode(self, scalar_input, dim) -> None:
        """Encodes the scalar input in the correspondent qubit.

        Example
        -------
        To encode a `sequence` of input vectors, given `tau` and `n`::

            for t in range(model.tau): # loop through time
                for dim in range(model.n): # loop through dimensions
                    model.encode(sequence[t][dim], dim)

        """

    def measure(self, shots=1, backend: Backend = None) -> Dict[str, int]:
        """Measures the qubits using a IBMQ backend

        Parameters
        ----------
        shots : int
            Number of times to repeat the measurement shot
        backend : qiskit Backend
            Quantum backend for the execution (if None, AER simulator is
            chosen as default)

        Returns
        ----------
        dict
            State occurrences counts in the form {"state": count}
        """
        # Initialize simulator if no backend is set
        backend = backend or qiskit.Aer.get_backend("aer_simulator")

        # Copy quantum circuit
        circ = self.circ.copy()
        # Add measure gates linking the all the qubits
        # to the corresponding classical bits
        all_bits = list(range(0, self.n))
        circ.measure(all_bits, all_bits)

        # Execute the circuit on the backend
        circ = qiskit.transpile(circ, backend)
        job: BaseJob = qiskit.execute(circ, backend, shots=shots)
        job_result: Result = job.result()
        counts_dict: dict[str, int] = job_result.get_counts(circ)

        return counts_dict

    @abstractmethod
    def decode(self) -> str:
        """Exploits the information encoded in the qubit."""

    @abstractmethod
    def query(self, target_vector) -> None:
        r"""Changes the basis of the quantum system choosing `target_vector`
        as the basis state \|00...0>."""

    def get_statevector(self) -> np.ndarray:
        """Returns the simulated state vector of the model.

        Returns
        ---------
        numpy.ndarray
            Model's state vector.
        """
        # Initialize simulator
        backend = qiskit.Aer.get_backend("aer_simulator_statevector")

        # Copy quantum circuit (without measure gates)
        circ = self.circ.copy()
        circ.save_statevector()

        # Transpile for simulator
        circ = qiskit.transpile(circ, backend)

        # Run and get statevector
        job: BaseJob = qiskit.execute(circ, backend)
        job_result: Result = job.result()
        statevector: Statevector = job_result.get_statevector(circ)

        return np.asarray(statevector)

    def get_density_matrix(self) -> np.ndarray:
        """Returns the simulated density matrix of the model.

        Returns
        ---------
        numpy.ndarray
            Model's density matrix.
        """
        # Initialize simulator
        backend: Backend = qiskit.Aer.get_backend("aer_simulator_unitary")

        # Copy quantum circuit (without measure gates)
        circ = self.circ.copy()
        circ.save_unitary()

        # Transpile for simulator
        circ = qiskit.transpile(circ, backend)

        # Run and get unitary operator
        job: BaseJob = qiskit.execute(circ, backend)
        job_result: Result = job.result()
        unitary_operator: Operator = job_result.get_unitary(circ)

        return np.asarray(unitary_operator)

    def print_circuit(self) -> None:
        """Prints the quantum circuit on which the model is implemented."""
        print(self.circ)

    def plot_state_mat(self) -> None:
        """Plots the state and density matrix of the quantum system
        (just the real parts).

        Example
        -------
        To plot a perfectly balanced superposition of states::

            model = Model(n, tau) # change Model with the desired child class

            for t in range(0,model.tau): # loop through time
                for dim in range(model.n): # loop through dimensions
                    model.encode(.5, dim)

            model.plot_state_mat()


        Raises
        ----------
        OverflowError
            If the dimension of the model is 6 or greater, plotting fails
            due to the high number of basis states.
        """
        if self.n >= 6:  # avoid matrices too big to be useful
            raise OverflowError(
                f"n={self.n} means {np.power(2,self.n)} states"
                + "(too much for a reasonable plot)!"
            )

        fig = plt.figure(figsize=(15, 4))

        # Plot the vector state
        axis = fig.add_subplot(121)
        state = pd.DataFrame(self.get_statevector().real)
        axis = sns.heatmap(
            state,
            annot=True,
            linewidths=0.5,
            xticklabels="",
            ax=axis,
            cmap="coolwarm",
            vmin=-1,
            vmax=1,
            fmt=".5g",
        )
        axis.set_title("State vector (real part)")

        # Plot the density matrix
        axis = fig.add_subplot(122)
        matrix = pd.DataFrame(self.get_density_matrix().real)
        axis = sns.heatmap(
            matrix,
            annot=True,
            linewidths=0.5,
            ax=axis,
            cmap="coolwarm",
            vmin=-1,
            vmax=1,
            fmt=".5g",
        )
        axis.set_title("Density Matrix (real part)")
