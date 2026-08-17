"""Tests for core abstract API contracts."""

import pytest

from qrobot.bursts.burst import Burst


def test_burst_is_abstract() -> None:
    """Only concrete bursts can be instantiated."""
    with pytest.raises(TypeError):
        Burst()


def test_abstract_burst_default_cannot_silently_return_none() -> None:
    """An incomplete subclass must fail rather than yield an invalid value."""

    class IncompleteBurst(Burst):
        def __call__(self, state: str) -> float:
            return super().__call__(state)

    with pytest.raises(NotImplementedError):
        IncompleteBurst()("0")
