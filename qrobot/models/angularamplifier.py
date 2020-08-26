import operator

from .angularmodel import AngularModel


class AngularAmplifier(AngularModel):
    """
    """

    def __init__(self, n, tau):
        """
        """
        AngularModel.__init__(self, n, tau)

    def query(self):
        """No query available for the AngularAmplifier, it just
        amplifies the results for the base state |00...0>.

        Raises:
            Warning: No query available for AngularAmplifier
        """
        raise Warning("No query available for AngularAmplifier")

    def encode(self, counts_dict):
        """Encodes every counts dictionary, not only the single-shot ones.
        """
        # Get the total number of counts (the measurement shots)
        tot_shots = sum(counts_dict.values())

        # Loop through the measurement results
        for key, count in counts_dict.items():
            # Get the input model's dimensionality
            input_n = len(key)
            # Check if it is compatible with amplifier's dimensionality
            if input_n != self.n:
                raise IndexError(f"The input model has n={input_n}, " +
                                 f"but the amplifier supports n={self.n}!")
            # For each i-th qubit of the model
            for i in range(input_n):
                # If the measurement is referring to the state "1"
                #   of the i-th qubit, encode that measurement in
                #   the i-th qubit of the amplifier (i+1 dimension).
                #   BEWARE: the state notation is "MSB...LSB", so we 
                #           start from the LSB, that is the "input_n"-th 
                #           character of the "key" string
                if key[input_n-1-i] == "1":
                    AngularModel.encode(self, input=count/tot_shots, dim=i+1)
                    print(f"{key}: {count/tot_shots} -> stored in {i+1}-th qubit")
