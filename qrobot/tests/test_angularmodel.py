import pytest
from qrobot.models import AngularModel


def test_init():
    """test that exceptions are raised for n and tau not being correct"""

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
    """test that exceptions are raised for input and dimension not being correct"""

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


def test_measure():
    """test that a certain measurements is carried out correctly"""

    model = AngularModel(n=1, tau=1)
    # Encode a full input on the dimension 1
    model.encode(1, 1)
    # check the measurement
    assert model.measure(shots=1) == {'1':1}

    model = AngularModel(n=1, tau=1)
    assert model.measure(shots=1) == {'0':1}

    model = AngularModel(n=3, tau=1)
    model.encode(1, 2)
    assert model.measure(shots=1) == {'010':1}
