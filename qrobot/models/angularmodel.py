import numpy as np

from .model import Model

class AngularModel(Model):
    """``AngularModel`` is a kind of ``Model`` which encodes the perceptual 
    information in the angle of the qubits' Bloch sphere representations
    """

    def encode(self, input, dim):
        """Encodes the input in the correspondent qubit

        Parameters
        ----------
        input : float
            The scalar input for a certain dimension, must be a number 
            between 0 and 1 inclusive.
        dim : int
            The model's dimension which the input belongs.

        Returns
        ----------
        float
            The rotation angle applied to the qubit.
        """

        # Check the argument dim
        if not isinstance(dim, int):
            raise TypeError("dim must be an integer!")
        if dim < 1:
            raise ValueError("dim must be greater than 0!")
        if dim > self.n:
            raise IndexError(f"dim out of bounds (dimensions = {self.n})!")

        # Check the argument input
        if not (isinstance(input, int) or isinstance(input, float)):
            raise TypeError(
                f"input must be an scalar number, not a {type(input)}!")
        if float(input) > 1 or float(input) < 0:
            raise ValueError("input must be between 0 and 1 inclusive!")

        # Apply rotation to the qubit
        angle = np.pi*input/self.tau
        # !!! Qubit index start at 0, dimensions at 1:
        self.circ.ry(angle, dim-1)
        return angle

    def query(self, target):
        """Changes the basis of the quantum system choosing target as 
        the basis state \|00...0>

        Parameters
        ----------
        target : list
            The target state, it must be a list containing n floats 
            (between 0 and 1 inclusive).
        """
        # Dimensionality check on the vector
        if len(target) is not self.n:
            raise ValueError(f"target must be a {self.n}-dimensional vector!")
        for element in target:
            if element > 1 or element < 0:
                raise ValueError(
                    f"target elements must be all between 0 and 1 inclusive!")

        # Apply negative (inverse) rotations to the qubit in order to
        # have the target state as the new |00...0> state.
        # Loop through all the dimensions:
        for i in range(0, self.n):
            angle = - np.pi*target[i]
            self.circ.ry(angle, i)

    def decode(self):
        """The decoding for the ``AngularModel`` is a single measurement."""
        return self.measure()

