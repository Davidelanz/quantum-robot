"""Linear-probability quantum-like perception model."""

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

        Use this method for one value in one dimension. Use
        :meth:`~qrobot.models.model.Model.encode_vector` to encode a complete
        multidimensional sample at once.

        Parameters
        ----------
        scalar_input : float
            Normalized input in the interval ``[0, 1]``.
        dim : int
            Zero-based input dimension.

        Returns
        -------
        float
            The rotation angle applied to the qubit.

        Examples
        --------
        Encode one value in dimension zero::

            model = LinearModel(n=2, tau=1)
            angle = model.encode(0.25, dim=0)

        Encode both dimensions together::

            angles = model.encode_vector([0.25, 0.75])
        """
        # Check the arguments
        dim = self._dim_index_check(dim)
        scalar_input = self._scalar_input_check(scalar_input)

        # Apply rotation to the qubit
        angle = (np.arcsin(2 * scalar_input - 1) + np.pi / 2) / self.tau
        self.circ.ry(angle, dim)
        return float(angle)
