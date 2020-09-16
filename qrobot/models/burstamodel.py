import operator

from .angularmodel import AngularModel

class BurstAModel(AngularModel):
    """``BurstAModel`` is a kind of ``AngularModel`` which returns a float,
    rather than a dictionary, as the decoded output.
    """

    def decode(self):
        r"""The decoding for the ``BurstAModel`` is \"burst\" between 0 and 1,
        which corresponds to the sum of the "zeros" in the measured state
        divided by the dimension n of the model. For example, if
        the measure is {"110101" = 1} the decoded burst is 2/6 = 0.333333333333


        Returns
        ----------
        float
            The burst, a value between 0 and 1 (the nearer to 0, the closer to
            the basis state \|00...0> )
        """
        # Get the measure
        measure = self.measure()  # in the form {"state": 1}

        # Get the key with max value (the "state"):
        state = max(measure.items(), key=operator.itemgetter(1))[0]

        # Number ones / total number chars
        output = state.count('0')/len(state)

        return output
