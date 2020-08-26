import numpy as np

from .model import Model
from .angularmodel import AngularModel

class LinearModel(Model):
    """``LinearModel`` corrects the ``AngularModel`` the encoding, allowing
    a linear decoding for single-event sequencies (tau=1).

    Notes
    -----
    The current implementation of ``LinearModel`` provides a linear
    dependency between encoded input and decoding probabilities
    only for tau = 1 (or for tau > 1 if and only if the input is always
    the same one). For a time-varying sequencee (tau > 1)
    the results obtained are again nonlinear, and similar to the 
    one of ``AngularModel``
    (see `this notebook <https://github.com/Davidelanz/quantum-robot/blob/master/notebooks/model_comparison.ipynb>`_
    for more information)

    """

    def encode(self, input, dim):
        """Encodes the input in the correspondent qubit

        Parameters
        ----------
        input : float
            The scalar input for a certain dimension, must be a number between
            0 and 1 inclusive.
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
        if input > 1 or input < 0:
            raise ValueError("input must be between 0 and 1 inclusive!")

        # Apply rotation to the qubit
        angle = (np.arcsin(2*input-1)+np.pi/2)/self.tau
        # !!! Qubit index start at 0, dimensions at 1:
        self.circ.ry(angle, dim-1)
        return angle

    def query(self, target):
        """Same query function as the ``AngularModel``

        See Also
        ----------
        AngularModel.query :
        """
        # Same as the Angular Model:
        AngularModel.query(self, target)

    def decode(self):
        """The decoding for the ``LinearModel`` is a single measurement."""
        dict =  self.measure()
        # Return the most measured state (only one measurement though)
        return max(dict, key=dict.get)
