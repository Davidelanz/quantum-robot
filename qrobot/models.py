import qiskit
import numpy as np
import matplotlib.pyplot as plt

QASM_BACKEND = qiskit.Aer.get_backend('qasm_simulator')

class AngularModel():
    """ 
    AngularModel is a class which embeds the angular model for QL perception

    ...

    Attributes
    ----------
    n : int
        the model dimension (greater than 0)
    tau : int
        number of samples of the temporal window (greater than 0)
    circ : qiskit.QuantumCircuit
        the quantum circuit which implements the model

    Methods
    -------
    encode(input, dim)
        encodes the input along a dimension in the correspondent qubit
    print()
        prints the quantum circuit on which the model is implemented
    plot_state()
        plots the state and density matrix of the quantum system
    """

    def __init__(self, n, tau):
        """Initialize the class"""

        # Check the argument n
        if isinstance(n, int):
            if n > 0:
                self.n = n
            else:
                raise ValueError("n must be greater than 0!")
        else:
            raise TypeError("n must be an integer!")

        # Check the argument tau
        if isinstance(tau, int):
            if tau > 0:
                self.tau = tau
            else:
                raise ValueError("tau must be greater than 0!")
        else:
            raise TypeError("tau must be an integer!")

        # Initialize the circuit
        self.circ = qiskit.QuantumCircuit(n, n)

    def encode(self, input, dim):
        """Encodes the input in the correspondent qubit

        Parameters:
            input (float): the input, must be a number between 0 and 1 inclusive
            dim (int): the model dimension which the input belongs

        Returns:
            angle (float): the rotation angle applied to the qubit
        """

        # Check the argument dim
        if not isinstance(dim, int):
            raise TypeError("dim must be an integer!")
        if dim < 1:
            raise ValueError("dim must be greater than 0!")
        if dim > self.n:
            raise IndexError(f"dim out of bounds (dimensions = {self.n})!")
        if input > 1 or input < 0:
            raise ValueError("input must be between 0 and 1 inclusive!")

        # Apply rotation to the qubit
        angle = np.pi*input/self.tau
        # !!! Qubit index start at 0, dimensions at 1:
        self.circ.ry(angle, dim-1)
        return angle

    def measure(self, shots=1, backend=QASM_BACKEND):
        """"""
        # Apply barrier
        self.circ.barrier()

        # Link the all the qubits to the corresponding classical bits
        all_bits = list(range(0, self.n))
        self.circ.measure(all_bits, all_bits)

        # Execute the circuit on the backend
        job = qiskit.execute(self.circ, backend, shots=shots)
        counts = job.result().get_counts(self.circ)

        return counts

    def decode(self):
        """"""
        return self.measure()


    def print(self):
        """Prints the quantum circuit on which the model is implemented"""
        print(self.circ)

    def plot_state(self):
        """Plots the state and density matrix of the quantum system"""
        plt.figure(figsize=(15, 4))

        # Plot the vector state
        ax1 = plt.subplot(1, 2, 1)
        state_backend = qiskit.Aer.get_backend('statevector_simulator')
        job = qiskit.execute(self.circ, state_backend).result()
        qiskit.visualization.plot_state_hinton(
            job.get_statevector(self.circ), ax_real=ax1)
        ax1.set_title("State vector")

        # Plot the density matrix
        ax2 = plt.subplot(1, 2, 2)
        matrix_backend = qiskit.Aer.get_backend('unitary_simulator')
        job = qiskit.execute(self.circ, matrix_backend).result()
        qiskit.visualization.plot_state_hinton(
            job.get_unitary(self.circ), ax_real=ax2)
        ax2.set_title("Density Matrix")

        plt.show()
