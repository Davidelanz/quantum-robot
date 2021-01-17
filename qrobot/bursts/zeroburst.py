from .burst import Burst


class ZeroBurst(Burst):
    """When called, ``ZeroBurst`` converts a measured state into
    a float number which is:

    .. math::

        \\frac{
            \\text{Number of 0s for the state in the computational base}
        }{
            \\text{State dimension}
        }

    For example, for ``"00100100"`` we have :math:`\\frac{6}{8}`:

    >>> from qrobot.bursts import ZeroBurst
    >>> state = "00100100"
    >>> ZeroBurst(state)
    0.75

    """

    def __call__(self, state: str) -> float:
        return state.count('0')/len(state)
