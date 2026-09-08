"""Tests for controller-independent and reproducible bug worlds."""

from collections import Counter

from qrobot_simulator.bug_world.robots.classical_bug import ClassicalBug
from qrobot_simulator.bug_world.world.bug_world import BugWorld


def idle_controller(readings: dict[str, float]) -> dict[str, float]:
    """Return a complete inactive action mapping."""
    return {
        "bite": 0.0,
        "forward": 0.0,
        "backward": 0.0,
        "rotate_left": 0.0,
        "rotate_right": 0.0,
    }


def test_world_runs_a_classical_bug_through_the_common_headless_path() -> None:
    """The world starts, commands, and stops a real brain without rendering."""
    world = BugWorld.demo(ClassicalBug(), seed=12)

    behaviors = world.run_robot_headless(duration=0.05, dt=0.01)

    assert isinstance(behaviors, Counter)
    assert sum(behaviors.values()) == 5
    assert world.elapsed == 0.05


def test_seed_replays_random_animal_motion() -> None:
    """Identical seeds reproduce the randomly wandering prey trajectory."""
    first = BugWorld.demo(ClassicalBug(), seed=31)
    second = BugWorld.demo(ClassicalBug(), seed=31)

    first.run_headless(idle_controller, duration=2.0, dt=0.05)
    second.run_headless(idle_controller, duration=2.0, dt=0.05)

    first_poses = [(robot.x, robot.y, robot.heading) for robot in first.robots]
    second_poses = [(robot.x, robot.y, robot.heading) for robot in second.robots]
    assert first_poses == second_poses


def test_recorded_run_contains_raw_state_and_controller_values() -> None:
    """A recorded run retains time series needed by later experiment analysis."""
    world = BugWorld.demo(ClassicalBug(), seed=7)

    record = world.run_recorded_headless(duration=0.03, dt=0.01)

    assert len(record.samples) == 3
    assert sum(record.behaviors.values()) == 3
    assert record.samples[-1].readings == world.readings
    assert "prey_evidence" in record.samples[-1].diagnostics
    assert record.samples[-1].predator_distance > 0.0
