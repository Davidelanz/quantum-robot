import numpy as np

from .model import Model


class AngularModel(Model):
    """``AngularModel`` is a kind of ``Model`` which encodes the perceptual
    information in the angle of the qubits' Bloch sphere representations
    """

    def encode(self, scalar_input, dim):
        """Encodes the scalar input in the correspondent qubit

        Parameters
        ----------
        input : float
            The scalar input for a certain dimension, must be a number
            between 0 and 1 inclusive.
        dim : int
            The model's dimension which the input belongs (values 
            between ``0`` and ``n-1``)

        Returns
        ----------
        float
            The rotation angle applied to the qubit.
        """
        # Check the arguments
        dim = self._dim_index_check(dim)
        scalar_input = self._scalar_input_check(scalar_input)

        # Apply rotation to the qubit
        angle = np.pi*scalar_input/self.tau
        self.circ.ry(angle, dim)
        return angle

    def query(self, target_vector):
        r"""Changes the basis of the quantum system choosing target_vector as
        the basis state \|00...0>

        Parameters
        ----------
        target_vector : list
            The target_vector state, it must be a list containing n floats
            (between 0 and 1 inclusive).
        """
        # Check the arguments
        target_vector = self._target_vector_check(target_vector)

        # Apply negative (inverse) rotations to the qubit in order to
        # have the target_vector state as the new |00...0> state.
        # Loop through all the dimensions:
        for i in range(0, self.n):
            angle = - np.pi*target_vector[i]
            self.circ.ry(angle, i)

    def decode(self):
        """The decoding for the ``AngularModel`` is a single measurement.
        
        Returns
        --------
        str 
            The string label corresponding to the decoded state
        
        """
        measure_dict = self.measure()
        # Return the most measured state (only one measurement though)
        return max(measure_dict, key=measure_dict.get)
