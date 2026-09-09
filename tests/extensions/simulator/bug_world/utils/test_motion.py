"""Tests for toroidal body integration."""

from qrobot_simulator.bug_world.utils.motion import integrate_motion


def test_motion_reports_and_wraps_a_boundary_crossing() -> None:
    """Crossing an edge is observable while the returned pose remains valid."""
    x, y, heading, crossed = integrate_motion(
        position=(9.6, 5.0),
        heading=0.0,
        radius=0.3,
        limits=(1.0, 1.0),
        commands=(1.0, 0.0),
        dt=0.2,
        bounds=(10.0, 10.0),
    )

    assert crossed
    assert 0.3 <= x <= 9.7
    assert y == 5.0
    assert heading == 0.0
