import numpy as np

from .angularmodel import AngularModel


class LinearModel(AngularModel):
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

    def encode(self, scalar_input, dim):
        """Encodes the scalar input in the correspondent qubit

        Parameters
        ----------
        scalar_input : float
            The scalar input for a certain dimension, must be a number between
            0 and 1 inclusive.
        dim : int
            The model's dimension which the scalar input belongs.

        Returns
        ----------
        float
            The rotation angle applied to the qubit.
        """
        # Check the arguments
        dim = self.dim_index_check(dim)
        scalar_input = self.scalar_input_check(scalar_input)

        # Apply rotation to the qubit
        angle = (np.arcsin(2*scalar_input-1)+np.pi/2)/self.tau
        # !!! Qubit index start at 0, dimensions at 1:
        self.circ.ry(angle, dim-1)
        return angle
