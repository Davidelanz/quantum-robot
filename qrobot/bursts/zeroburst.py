from .burst import Burst


class ZeroBurst(Burst):
    """When called ``Burst`` converts a measured state into 
    a float number which is (number of **zeroes** for the state in
    the computational base)/(state dimension)
    """

    def __call__(self, state: str) -> float:
        """ Given a basis state in computational basis
        returns a float number which is the number of **zeroes** for the state
        in the computational base divided by the dimension of the state.

        Parameters
        -----------
        state : str
            The state string representaton in computational basis (e.g. "01010")

        Returns
        ---------
        float
            The burst based on the input state
        """
        return state.count('0')/len(state)
