"""Angular quantum-like perception model."""

import numpy as np

from .model import Model, Scalar, TargetVector


class AngularModel(Model):
    """Encode normalized inputs as Bloch-sphere rotation angles.

    Each sample contributes ``scalar_input * pi / tau`` to the qubit assigned
    to its input dimension.
    """

    def encode(self, scalar_input: Scalar, dim: int) -> float:
        """Encode one scalar input as a fractional y-axis rotation.

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

            model = AngularModel(n=2, tau=1)
            angle = model.encode(0.25, dim=0)

        Encode both dimensions together::

            angles = model.encode_vector([0.25, 0.75])
        """
        # Check the arguments
        dim = self._dim_index_check(dim)
        scalar_input = self._scalar_input_check(scalar_input)

        # Apply rotation to the qubit
        angle = np.pi * scalar_input / self.tau
        self.circ.ry(angle, dim)
        return angle

    def query(self, target_vector: TargetVector) -> None:
        r"""Change basis so ``target_vector`` maps to state \|00...0>.

        Parameters
        ----------
        target_vector : list
            Normalized target value for every model dimension.
        """
        # Check the arguments
        target_vector = self._target_vector_check(target_vector)

        # Apply negative (inverse) rotations to the qubit in order to
        # have the target_vector state as the new |00...0> state.
        # Loop through all the dimensions:
        for i in range(0, self.n):
            angle = -np.pi * target_vector[i]
            self.circ.ry(angle, i)

    def decode(self) -> str:
        """Decode the model with one computational-basis measurement.

        Returns
        -------
        str
            Measured basis-state bit string.

        """
        measure_dict = self.measure()
        # A one-shot count dictionary contains one observed state.
        return max(measure_dict, key=lambda state: measure_dict[state])
