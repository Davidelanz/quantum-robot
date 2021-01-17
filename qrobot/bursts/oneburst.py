from .burst import Burst


class OneBurst(Burst):
    """When called, ``ZeroBurst`` converts a measured state into
    a float number which is:

    .. math::

        \\frac{
            \\text{Number of 1s for the state in the computational base}
        }{
            \\text{State dimension}
        }

    For example, for ``"00100100"`` we have :math:`\\frac{2}{8}`:

    >>> from qrobot.bursts import OneBurst
    >>> state = "00100100"
    >>> OneBurst(state)
    0.25

    """

    def __call__(self, state: str) -> float:
        return state.count('1')/len(state)
