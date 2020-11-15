import pytest
from ..models import BurstAModel


def test_init():
    """Tests if exceptions are raised for n and tau not being correct"""

    # Testing wrong n
    with pytest.raises(TypeError):
        assert BurstAModel(n=1.2, tau=2)
    with pytest.raises(ValueError):
        assert BurstAModel(n=-1, tau=3)
    with pytest.raises(ValueError):
        assert BurstAModel(n=0, tau=2)

    # Testing wrong tau
    with pytest.raises(TypeError):
        assert BurstAModel(n=1, tau=1.2)
    with pytest.raises(ValueError):
        assert BurstAModel(n=5, tau=0)


def test_encode():
    """Tests if exceptions are raised for input and dimension not being correct"""

    model = BurstAModel(n=2, tau=2)

    # Testing correct way of use encode
    model.encode(.55, 1)

    # Testing wrong input
    with pytest.raises(TypeError):
        assert model.encode([.1, .2], 1)
    with pytest.raises(TypeError):
        assert model.encode("a", 1)
    with pytest.raises(ValueError):
        assert model.encode(1.1, 0)
    with pytest.raises(ValueError):
        assert model.encode(-0.1, 0)

    # Testing wrong dim
    with pytest.raises(TypeError):
        assert model.encode(.55, 2.1)
    with pytest.raises(ValueError):
        assert model.encode(.55, -1)
    with pytest.raises(IndexError):
        assert model.encode(.55, 2)


def test_decode():
    """Tests decoding for unambiguous inputs"""

    model = BurstAModel(n=1, tau=1)
    input_data = 1  # unambiguous input
    model.encode(input_data, dim=0)
    # the measure is {'1': 1} -> decode should be 0/1
    assert round(model.decode(), 10) == round(0/1, 10)

    model = BurstAModel(n=1, tau=1)
    input_data = 0  # unambiguous input
    model.encode(input_data, dim=0)
    # the measure is {'0': 1}
    assert round(model.decode(), 10) == round(1/1, 10)

    model = BurstAModel(n=3, tau=1)
    input_data = 1  # unambiguous input
    model.encode(input_data, dim=1)
    # the measure is {'010': 1}
    assert round(model.decode(), 10) == round(2/3, 10)

    model = BurstAModel(n=5, tau=3)
    # prepare the input
    input_data = list()
    for _ in range(0, model.tau):
        input_data.append([1, 0, 1, 0, 1])
    # encode it
    for t in range(model.tau):
        for dim in range(model.n):
            model.encode(input_data[t][dim], dim)
    # decode it
    assert round(model.decode(), 10) == round(2/5, 10)


def test_query():
    """Tests query on the input itself"""

    # 1-dimensional model
    model = BurstAModel(n=1, tau=1)
    # Define an input data value
    input_data = 1
    # Encode input_data one time (tau = 1)
    model.encode(input_data, dim=0)
    # Apply a query on the input_data (to obtain an unambiguous result)
    model.query(input_data)
    # See if the actual output is the |00...0> state
    assert model.decode() == 1

    # 3-dimensional model, 2-events time window
    model = BurstAModel(n=5, tau=2)
    # Define an input data value
    input_data = [.1, .4, .5, .2, .1]
    # Encode input_data two times (tau = 1)
    for _ in range(model.tau):
        for dim in range(model.n):
            model.encode(input_data[dim], dim)
    # Apply a query on the input_data (to obtain an unambiguous result)
    model.query(input_data)
    # See if the actual output is the |00...0> state or a close one (ar most one zero)
    assert round(model.decode(), 10) == round(0/5, 10) or round(1/5, 10)

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
    model = BurstAModel(1, 1)
    model.print_circuit()
    model.plot_state_mat()


def test_probabilities():
    """Tests aggregated probabilities for multiple measurementr in a workflow."""

    # 3-dimensional model, 2-events time window
    model = BurstAModel(3, 2)
    # Define an input data sequence (tau = 2)
    input_data = list()
    input_data.append([0.8, 0.8, 1])
    input_data.append([0.9, 0.6, .9])
    # Encode the sequence in the model
    for i in range(model.tau):
        for dim in range(model.n):
            model.encode(input_data[i][dim], dim)
    # Check if at least 70% of the shots are 111 (coherent with the input)
    shots = 10000
    result = model.measure(shots)
    assert result['111']/shots >= .7

    # Check again for a different input
    model.clear()
    # Define an input data sequence (tau = 2)
    input_data = list()
    input_data.append([0.1, 0.2, 1])
    input_data.append([0.0, 0.1, .9])
    # Encode the sequence in the model
    for i in range(model.tau):
        for dim in range(model.n):
            model.encode(input_data[i][dim], dim)
    # Check if at least 70% of the shots are 111 (coherent with the input)
    result = model.measure(shots)
    assert result['100']/shots >= .8
