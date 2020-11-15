from abc import ABC, abstractmethod

import qiskit
import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
import seaborn as sns


QASM_BACKEND = qiskit.Aer.get_backend('qasm_simulator')
""" qiskit backend: Module-level qiskit backend variable for quantum circuit
simulation on local classical hardware via QASM simulator.
"""


class Model(ABC):
    """ ``Model`` is an abstract class which embeds the general features
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

    def __init__(self, n, tau):
        """Initialize the class"""

        # Check the argument n
        if isinstance(n, int):
            if n > 0:
                self.n = n
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

    def clear(self):
        """Re-initialize the model with an empty circuit."""
        self.circ = qiskit.QuantumCircuit(self.n, self.n)

    @abstractmethod
    def encode(self, scalar_input, dim):
        """Encodes the scalar input in the correspondent qubit.

        Example
        -------
        To encode a `sequence` of input vectors, given `tau` and `n`::

            for t in range(model.tau): # loop through time
                for dim in range(model.n): # loop through dimensions
                    model.encode(sequence[t][dim], dim)

        """

    def dim_index_check(self, dim):
        """This method ensures that a dimension index `dim`
        is an integer between 1 and `n`, where `n` is the dimension
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

    def scalar_input_check(self, scalar_input):
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
                f"input must be an scalar number, not a {type(scalar_input)}!")
        if scalar_input > 1 or scalar_input < 0:
            raise ValueError("scalar_input must be between 0 and 1 inclusive!")
        return scalar_input

    def measure(self, shots=1, backend=QASM_BACKEND):
        """Measures the qubits using a IBMQ backend

        Parameters
        ----------
        shots : int
            Number of measurement shots
        backend : qiskit backend
            Quantum backend for the execution (QASM simulator as default)

        Returns
        ----------
        dict
            State occurrences counts in the form {"state": count}
        """

        # Apply barrier
        self.circ.barrier()

        # Link the all the qubits to the corresponding classical bits
        all_bits = list(range(0, self.n))
        self.circ.measure(all_bits, all_bits)

        # Execute the circuit on the backend
        job = qiskit.execute(self.circ, backend, shots=shots)
        counts = job.result().get_counts(self.circ)

        return counts

    @abstractmethod
    def query(self, target_vector):
        r"""Changes the basis of the quantum system choosing `target_vector`
        as the basis state \|00...0>."""

    def target_vector_check(self, target_vector):
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
        # If target_vector is a single number, convert it in a single-element vector
        if isinstance(target_vector, (float, int)):
            target_vector = [target_vector]
        # Dimensionality check on the vector
        if len(target_vector) is not self.n:
            raise ValueError(f"target_vector must be a {self.n}\
                             -dimensional vector!")
        for element in target_vector:
            if not isinstance(element, (float, int)):
                raise TypeError(
                    "target_vector elements must be all integers or floats!")
            if element > 1 or element < 0:
                raise ValueError(
                    "target_vector elements must be all between \
                    0 and 1 inclusive!")
        return target_vector

    @abstractmethod
    def decode(self):
        """Exploits the information encoded in the qubit."""

    def get_state(self):
        """Returns the simulated state vector of the model.

        Returns
        ---------
        numpy.ndarray
            Model's state vector.
        """
        state_simulator = qiskit.Aer.get_backend('statevector_simulator')
        simulation = qiskit.execute(self.circ, state_simulator).result()
        return simulation.get_statevector(self.circ)

    def get_density(self):
        """Returns the simulated density matrix of the model.

        Returns
        ---------
        numpy.ndarray
            Model's density matrix.
        """
        matrix_simulator = qiskit.Aer.get_backend('unitary_simulator')
        simulation = qiskit.execute(self.circ, matrix_simulator).result()
        return simulation.get_unitary(self.circ)

    def print_circuit(self):
        """Prints the quantum circuit on which the model is implemented."""
        print(self.circ)

    def plot_state_mat(self):
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
                f"n={self.n} means {np.power(2,self.n)} states" +
                "(too much for a reasonable plot)!")

        fig = plt.figure(figsize=(15, 4))

        # Plot the vector state
        axis = fig.add_subplot(121)
        state = pd.DataFrame(self.get_state().real)
        axis = sns.heatmap(state, annot=True, linewidths=.5, xticklabels="",
                           ax=axis, cmap="coolwarm", vmin=-1, vmax=1, fmt=".5g")
        axis.set_title("State vector (real part)")

        # Plot the density matrix
        axis = fig.add_subplot(122)
        matrix = pd.DataFrame(self.get_density().real)
        axis = sns.heatmap(matrix, annot=True, linewidths=.5,
                           ax=axis, cmap="coolwarm", vmin=-1, vmax=1, fmt=".5g")
        axis.set_title("Density Matrix (real part)")

        # return fig
