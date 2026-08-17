"""Tests for the optional model-visualization integration boundary."""

import sys

import pytest

from qrobot.models import AngularModel


def test_plot_explains_missing_visualization_extra(monkeypatch) -> None:
    """Core users receive an actionable error without plotting dependencies."""
    monkeypatch.setitem(sys.modules, "matplotlib", None)

    with pytest.raises(ImportError, match="model-visualization"):
        AngularModel(1, 1).plot_state_mat()
