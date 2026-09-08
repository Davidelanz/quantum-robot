"""Tests for common normalized-action interpretation."""

import pytest

from qrobot_simulator.bug_world.robots.config import BaseBugConfig
from qrobot_simulator.bug_world.utils.actions import behavior_label, motion_commands


def test_opposing_actions_become_signed_body_commands() -> None:
    """Shared gains combine forward/backward and left/right consistently."""
    actions = {
        "bite": 0.8,
        "forward": 0.7,
        "backward": 0.2,
        "rotate_left": 0.1,
        "rotate_right": 0.4,
    }

    speed, turn, biting = motion_commands(actions, BaseBugConfig())

    assert speed == pytest.approx(0.5)
    assert turn == pytest.approx(-0.3)
    assert biting
    assert behavior_label(speed, turn, actions["forward"], biting) == "BITE"
