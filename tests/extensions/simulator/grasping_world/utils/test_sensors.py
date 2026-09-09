"""Grasping sensor-mapping tests."""

import pytest

from qrobot_simulator.grasping_world.utils.sensors import proximity_reading, touch_reading


@pytest.mark.parametrize(
    ("distance", "expected"),
    [(0.0, 1.0), (5.0, 1.0), (12.5, 0.5), (20.0, 0.0), (30.0, 0.0)],
)
def test_proximity_reading_is_clamped(distance: float, expected: float) -> None:
    """Distances map linearly between near and far and clamp outside them."""
    assert proximity_reading(distance, near=5.0, far=20.0) == pytest.approx(expected)


def test_proximity_reading_rejects_reversed_limits() -> None:
    """An invalid sensing interval is rejected."""
    with pytest.raises(ValueError, match="far must be greater"):
        proximity_reading(10.0, near=20.0, far=5.0)


def test_touch_reading_represents_empty_gripper() -> None:
    """Pressed touch is zero because the modeled feature is emptiness."""
    assert touch_reading(True) == 0.0
    assert touch_reading(False) == 1.0
