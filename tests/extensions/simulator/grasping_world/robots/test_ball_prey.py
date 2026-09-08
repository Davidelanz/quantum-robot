"""Bounded random motion of the ball prey."""

from dataclasses import replace
from random import Random

import pytest

from qrobot_simulator.grasping_world.robots.ball_prey import BallPrey
from qrobot_simulator.grasping_world.robots.config import BALL_PREY_CONFIG


def test_ball_leaves_near_zone_after_bounded_dwell() -> None:
    """A prolonged near visit overrides random drift with outward motion."""
    config = replace(BALL_PREY_CONFIG, max_near_duration=0.1, escape_speed=4.0)
    ball = BallPrey(0.0, 0.0, distance=10.0, velocity=0.0, config=config)
    rng = Random(1)

    # The first step starts the near-zone clock. Once its configured duration
    # expires, the second step must command motion away from the gripper.
    ball.step(0.01, 0.01, 5.0, None, rng, near_limit=15.0)
    ball.step(0.12, 0.01, 5.0, None, rng, near_limit=15.0)

    assert ball.velocity >= 4.0


@pytest.mark.parametrize(
    ("distance", "velocity", "expected_distance", "expected_sign"),
    [(5.1, -2.0, 5.0, 1.0), (44.9, 2.0, 45.0, -1.0)],
)
def test_ball_bounces_at_both_distance_limits(
    distance: float,
    velocity: float,
    expected_distance: float,
    expected_sign: float,
) -> None:
    """The prey remains outside the gripper base and inside sensor space."""
    ball = BallPrey(0.0, 0.0, distance=distance, velocity=velocity)
    rng = Random(3)
    ball.schedule_motion_change(0.0, rng)

    # A tenth of a second crosses the selected boundary. Scheduling the next
    # random change first isolates collision handling from velocity noise.
    ball.step(0.0, 0.1, 5.0, None, rng)

    assert ball.distance == pytest.approx(expected_distance)
    assert ball.velocity * expected_sign > 0
