import pytest
from ..models import LinearModel


def test_init():
    """Tests if exceptions are raised for n and tau not being correct"""

    # Testing wrong n
    with pytest.raises(TypeError):
        assert LinearModel(n=1.2, tau=2)
    with pytest.raises(ValueError):
        assert LinearModel(n=-1, tau=3)
    with pytest.raises(ValueError):
        assert LinearModel(n=0, tau=2)

    # Testing wrong tau
    with pytest.raises(TypeError):
        assert LinearModel(n=1, tau=1.2)
    with pytest.raises(ValueError):
        assert LinearModel(n=5, tau=0)


def test_encode():
    """Tests if exceptions are raised for input and dimension not being correct"""

    model = LinearModel(n=2, tau=2)

    # Testing correct way of use encode
    model.encode(.55, 1)

    # Testing wrong input
    with pytest.raises(TypeError):
        assert model.encode([.1, .2], 2)
    with pytest.raises(TypeError):
        assert model.encode("a", 2)
    with pytest.raises(ValueError):
        assert model.encode(1.1, 2)
    with pytest.raises(ValueError):
        assert model.encode(-0.1, 2)

    # Testing wrong dim
    with pytest.raises(TypeError):
        assert model.encode(.55, 2.1)
    with pytest.raises(ValueError):
        assert model.encode(.55, -1)
    with pytest.raises(IndexError):
        assert model.encode(.55, 4)


def test_decode():
    """Tests decoding for unambiguous inputs"""

    model = LinearModel(n=1, tau=1)
    input_data = 1  # unambiguous input
    model.encode(input_data, dim=1)
    assert model.decode() == '1'

    model = LinearModel(n=1, tau=1)
    input_data = 0  # unambiguous input
    model.encode(input_data, dim=1)
    assert model.decode() == '0'

    model = LinearModel(n=3, tau=1)
    input_data = 1  # unambiguous input
    model.encode(input_data, dim=2)
    assert model.decode() == '010'


def test_query():
    """Tests query on the input itself"""

    # 1-dimensional model
    model = LinearModel(n=1, tau=1)
    # Define an input data value
    input_data = 1
    # Encode input_data one time (tau = 1)
    model.encode(input_data, dim=1)
    # Apply a query on the input_data (to obtain an unambiguous result)
    model.query(input_data)
    # See if the actual output is the |00...0> state
    assert model.decode() == '0'

    # 3-dimensional model, 2-events time window
    model = LinearModel(n=5, tau=2)
    # Define an input data value
    input_data = [.1, .4, .5, .2, .1]
    # Encode input_data two times (tau = 1)
    for _ in range(1, model.tau):
        for dim in range(1, model.n):
            model.encode(input_data[dim-1], dim)
    # Apply a query on the input_data (to obtain an unambiguous result)
    model.query(input_data)
    # See if the actual output is the |00...0> state
    assert model.decode() == '00000' or\
                             '10000' or\
                             '01000' or\
                             '00100' or\
                             '00010' or\
                             '00001'

    # Check the exception for wrong targets:
    with pytest.raises(ValueError):
        assert model.query([1, .2])  # size < n
    with pytest.raises(ValueError):
        assert model.query([1, .2, 0, 0, 0, 1, .2, 0])  # size > n

    # Check the exception for wrong target elements:
    with pytest.raises(ValueError):
        assert model.query([.1, .4, 5, .2, .1])  # third element is a 5


def test_plot():
    """Tests if the print and plot functions cause any error"""
    model = LinearModel(1, 1)
    model.print_circuit()
    model.plot_state_mat()


def test_probabilities():
    """Tests aggregated probabilities for multiple measurementr in a workflow."""

    # 3-dimensional model, 2-events time window
    model = LinearModel(3, 2)
    # Define an input data sequence (tau = 2)
    input_data = list()
    input_data.append([0.92, 0.91, 0.92])
    input_data.append([0.91, 0.92, 0.93])
    # Encode the sequence in the model
    for i in range(0, model.tau):
        for dim in range(1, model.n+1):
            model.encode(input_data[i][dim-1], dim)
    # Check if at least 70% of the shots are 111 (coherent with the input)
    shots = 10000
    result = model.measure(shots)
    print(result)
    assert result['111']/shots >= .7

    # Check again for a different input
    model.clear()
    # Define an input data sequence (tau = 2)
    input_data = list()
    input_data.append([0.1, 0.2, 1])
    input_data.append([0.0, 0.1, .9])
    # Encode the sequence in the model
    for i in range(0, model.tau):
        for dim in range(1, model.n+1):
            model.encode(input_data[i][dim-1], dim)
    # Check if at least 70% of the shots are 111 (coherent with the input)
    result = model.measure(shots)
    assert result['100']/shots >= .8
