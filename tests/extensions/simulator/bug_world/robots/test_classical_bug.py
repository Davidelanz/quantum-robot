"""Tests for the explicit classical bug controller."""

from qrobot_simulator.bug_world.robots.classical_bug import ClassicalBugBrain


def readings(**changes: float) -> dict[str, float]:
    """Return a complete neutral sensor snapshot with selected changes."""
    values = {
        "proximity": 0.0,
        "lr": 0.0,
        "lg": 0.0,
        "lb": 0.0,
        "rr": 0.0,
        "rg": 0.0,
        "rb": 0.0,
    }
    values.update(changes)
    return values


def test_classical_brain_approaches_blue_and_bites_only_when_close() -> None:
    """Blue evidence steers approach while proximity gates physical biting."""
    brain = ClassicalBugBrain()

    far = brain.command(readings(lb=0.8), 0.1)
    close = brain.command(readings(proximity=1.0, lb=0.8), 0.1)

    assert far["forward"] == 0.8
    assert far["rotate_left"] == 0.8
    assert far["bite"] == 0.0
    assert close["bite"] == 1.0


def test_classical_brain_turns_away_and_retreats_from_red() -> None:
    """A threat on the left produces backward and right-turn activations."""
    brain = ClassicalBugBrain()

    actions = brain.command(readings(lr=0.9), 0.1)

    assert actions["backward"] == 0.9
    assert actions["rotate_right"] == 0.9
    assert brain.diagnostics()["threat_evidence"] == 0.9
