from abc import ABC, abstractmethod
from collections.abc import Generator, Sequence
from typing import TypeAlias

import numpy as np

from qrobot.backends import QiskitBackend, QuantumBackend

Scalar: TypeAlias = float | int
TargetVector: TypeAlias = Sequence[Scalar] | Scalar


class Model(ABC):
    """Base class for quantum-like perception models.

    A model encodes an ``n``-dimensional sequence over ``tau`` samples in a
    quantum circuit. Subclasses define the input-to-rotation mapping, query
    transformation, and decoding rule.


    Parameters
    ----------
    n : int
        Number of input dimensions. Each dimension is represented by one qubit.
    tau : int
        Number of samples encoded in one temporal window.

    Attributes
    ----------
    n : int
        Model's dimension.
    tau : int
        Number of samples of the temporal window.
    circ : object
        Backend-specific circuit containing the encoded window.
    """

    def __init__(self, n: int, tau: int, backend: QuantumBackend | None = None) -> None:
        """Create an empty ``n``-qubit model for ``tau`` samples."""

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

        self.backend = backend or QiskitBackend()
        self.circ = self.backend.create_circuit(n)

    def __iter__(self) -> Generator[tuple[str, object], None, None]:
        yield "model", self.__class__.__name__
        yield "n", self.n
        yield "tau", self.tau

    def __repr__(self) -> str:
        out_str = "["
        for key, value in dict(self).items():
            out_str += f"{key}: {value}, "
        return out_str[:-2] + "]"

    def _dim_index_check(self, dim: int) -> int:
        """Validate and return an input-dimension index.

        Raises
        ---------
        TypeError
            `dim` is not an integer `int`
        ValueError
            ``dim`` is negative.
        IndexError
            ``dim`` is greater than or equal to ``n``.

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
            raise IndexError(f"dim is greater than the model dimension n={self.n}!")
        return dim

    @staticmethod
    def _scalar_input_check(scalar_input: Scalar) -> float:
        """Validate and normalize one scalar model input.

        Raises
        ---------
        TypeError:
            ``scalar_input`` is neither an ``int`` nor a ``float``.
        ValueError
            `scalar_input` is not between 0 and 1 inclusive

        Returns
        --------
        float
            The `scalar_input`
        """
        if not isinstance(scalar_input, (float, int)):
            raise TypeError(f"input must be a scalar number, not a {type(scalar_input)}!")
        if scalar_input > 1 or scalar_input < 0:
            raise ValueError("scalar_input must be between 0 and 1 inclusive!")
        return float(scalar_input)

    def _target_vector_check(self, target_vector: TargetVector) -> list[float]:
        """Validate a query target and return it as a list of floats.

        A scalar target is accepted for a one-dimensional model. Vector
        targets must contain exactly one normalized value per model dimension.

        Raises
        ---------
        TypeError
            `target_vector` elements are not all integers or floats
        ValueError
            `target_vector` dimension does not match model's dimension `n`
        ValueError
            A ``target_vector`` element is outside the interval ``[0, 1]``.

        Returns
        ----------
        list
            The `target_vector`
        """
        # Use the same validation path for scalar and vector targets.
        if isinstance(target_vector, (float, int)):
            target_vector = [target_vector]
        else:
            target_vector = list(target_vector)
        # Dimensionality check on the vector
        if len(target_vector) != self.n:
            raise ValueError(f"target_vector must be a {self.n}-dimensional vector!")
        for element in target_vector:
            if not isinstance(element, (float, int)):
                raise TypeError("target_vector elements must be all integers or floats!")
            if element > 1 or element < 0:
                raise ValueError("target_vector elements must be all between 0 and 1 inclusive!")
        return [float(element) for element in target_vector]

    def clear(self) -> None:
        """Re-initialize the model with an empty circuit."""
        self.circ = self.backend.create_circuit(self.n)

    @abstractmethod
    def encode(self, scalar_input: Scalar, dim: int) -> float:
        """Encode one normalized input in the qubit for ``dim``.

        Example
        -------
        To encode a `sequence` of input vectors, given `tau` and `n`::

            for t in range(model.tau): # loop through time
                for dim in range(model.n): # loop through dimensions
                    model.encode(sequence[t][dim], dim)

        """

    def measure(self, shots: int = 1) -> dict[str, int]:
        """Measure the qubits using the configured backend.

        Parameters
        ----------
        shots : int
            Number of times to repeat the measurement shot
        Returns
        ----------
        dict
            State occurrences counts in the form {"state": count}
        """
        return self.backend.sample_counts(self.circ, shots)

    @abstractmethod
    def decode(self) -> str:
        """Measure and decode the model state as a basis-state label."""

    @abstractmethod
    def query(self, target_vector: TargetVector) -> None:
        r"""Change basis so ``target_vector`` maps to state \|00...0>."""

    def get_statevector(self) -> np.ndarray:
        """Returns the simulated state vector of the model.

        Returns
        ---------
        numpy.ndarray
            Model's state vector.
        """
        return self.backend.statevector(self.circ)

    def get_density_matrix(self) -> np.ndarray:
        """Returns the simulated density matrix of the model.

        Returns
        ---------
        numpy.ndarray
            Model's density matrix.
        """
        statevector = self.get_statevector()
        return np.outer(statevector, statevector.conjugate())

    def print_circuit(self) -> None:
        """Prints the quantum circuit on which the model is implemented."""
        print(self.circ)

    def plot_state_mat(self) -> None:
        """Plot the real parts of the state vector and density matrix.

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
                f"n={self.n} means {np.power(2, self.n)} states"
                + "(too much for a reasonable plot)!"
            )

        # Plotting dependencies are loaded at the presentation boundary.
        try:
            import matplotlib.pyplot as plt
            import pandas as pd
            import seaborn as sns
        except ImportError as exc:
            raise ImportError(
                "plot_state_mat() requires the 'model-visualization' extra. "
                "Install it with 'poetry install --extras model-visualization'."
            ) from exc

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
