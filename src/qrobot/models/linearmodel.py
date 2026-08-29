import numpy as np

from .angularmodel import AngularModel
from .model import Scalar


class LinearModel(AngularModel):
    """Map a single normalized input linearly to measurement probability.

    Warning
    ----------
    For ``tau == 1``, measuring ``1`` has probability ``scalar_input``. A
    constant input repeated over a longer window has the same relationship.
    Time-varying windows accumulate inverse-sine rotation angles, so their
    measurement probability is generally not the arithmetic mean of the inputs.
    """

    def encode(self, scalar_input: Scalar, dim: int) -> float:
        """Encode one scalar input using the linear-probability angle map.

        Parameters
        ----------
        scalar_input : float
            Normalized input in the interval ``[0, 1]``.
        dim : int
            Zero-based input dimension.

        Returns
        ----------
        float
            The rotation angle applied to the qubit.
        """
        # Check the arguments
        dim = self._dim_index_check(dim)
        scalar_input = self._scalar_input_check(scalar_input)

        # Apply rotation to the qubit
        angle = (np.arcsin(2 * scalar_input - 1) + np.pi / 2) / self.tau
        self.circ.ry(angle, dim)
        return float(angle)
