import pytest
from qrobot.models import AngularModel


def test_init():
    """Tests if exceptions are raised for n and tau not being correct"""

    # Testing wrong n
    with pytest.raises(TypeError):
        assert AngularModel(n=1.2, tau=2)
    with pytest.raises(ValueError):
        assert AngularModel(n=-1, tau=3)
    with pytest.raises(ValueError):
        assert AngularModel(n=0, tau=2)

    # Testing wrong tau
    with pytest.raises(TypeError):
        assert AngularModel(n=1, tau=1.2)
    with pytest.raises(ValueError):
        assert AngularModel(n=5, tau=0)


def test_encode():
    """Tests if exceptions are raised for input and dimension not being correct"""

    model = AngularModel(n=2, tau=2)

    # Testing correct way of use encode
    model.encode(.55, 1)

    # Testing wrong input
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

    model = AngularModel(n=1, tau=1)
    input_data = 1  # unambiguous input
    model.encode(input_data, dim=1)
    assert model.decode() == {'1': 1}

    model = AngularModel(n=1, tau=1)
    input_data = 0  # unambiguous input
    model.encode(input_data, dim=1)
    assert model.decode() == {'0': 1}

    model = AngularModel(n=3, tau=1)
    input_data = 1  # unambiguous input
    model.encode(input_data, dim=2)
    assert model.decode() == {'010': 1}


def test_query():
    """Tests query on the input itself"""

    # 3-dimensional model, 2-events time window
    model = AngularModel(n=5, tau=1)

    # Define an input data value (tau = 1)
    input_data = [.1, .4, .5, .2, .1]

    # Encode input_data
    for dim in range(1, model.n):
        model.encode(input_data[dim-1], dim)

    # Apply a query on the input_data (to obtain an unambiguous result)
    model.query(input_data)

    # See if the actual output is the |00...0> state
    assert model.decode() == {'00000': 1}

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
    model = AngularModel(1, 1)
    model.print()
    model.plot_state()


def test_workflow1():
    """Tests if a full encode-decode workflow is carried out correctly"""

    # 3-dimensional model, 2-events time window
    model = AngularModel(3, 2)

    # Define an input data sequence (tau = 2)
    input_data = list()
    input_data.append([0.8, 0.8, 1])
    input_data.append([0.9, 0.6, .9])

    # Encode the sequence in the model
    for t in range(0, model.tau):
        for dim in range(1, model.n+1):
            model.encode(input_data[t][dim-1], dim)

    # Check if at least 70% of the shots are 111 (coherent with the input)
    shots = 10000
    result = model.measure(shots)
    assert result['111']/shots >= .7

    # Check again for a different input
    model = AngularModel(3, 2)
    input_data = list()
    input_data.append([0.1, 0.2, 1])
    input_data.append([0.0, 0.1, .9])
    for t in range(0, model.tau):
        for dim in range(1, model.n+1):
            model.encode(input_data[t][dim-1], dim)
    result = model.measure(shots)
    assert result['100']/shots >= .8
