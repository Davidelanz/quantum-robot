"""Headless wiring, sensing, and scoring in the grasping world."""

from dataclasses import replace

import pytest

from qrobot_simulator.grasping_world.robots.ball_prey import BallPrey
from qrobot_simulator.grasping_world.robots.classical_gripper import ClassicalGripper
from qrobot_simulator.grasping_world.robots.reactive_gripper import ReactiveGripper
from qrobot_simulator.grasping_world.world.grasping_world import GraspingWorld
from qrobot_simulator.grasping_world.robots.config import BALL_PREY_CONFIG
from qrobot_simulator.grasping_world.world.config import WORLD_CONFIG


def test_headless_callback_advances_without_rendering() -> None:
    """The callback API advances time without inventing grasp events."""
    world = GraspingWorld.demo(ClassicalGripper(), seed=7)

    # A permanently open command isolates integration from controller behavior.
    returned = world.run_headless(lambda readings: 0.0, duration=0.05, dt=0.01)

    assert returned is world
    assert world.elapsed == pytest.approx(0.05)
    assert world.correct_grips == 0


def test_world_runs_a_classical_gripper_without_an_adapter() -> None:
    """The native timed-controller path passes readings and time consistently."""
    world = GraspingWorld.demo(gripper=ClassicalGripper(), seed=4)

    world.run_robot_headless(duration=0.05, dt=0.01)

    assert world.elapsed == pytest.approx(0.05)


def test_robot_closure_is_scored_as_a_catch() -> None:
    """A grippable ball links controller closure to contact and score state."""
    gripper = ReactiveGripper()
    world = GraspingWorld.demo(gripper=gripper, seed=4)

    # Place stationary prey inside the jaws to isolate the closing transition
    # from the independent random-motion policy.
    world.ball.distance = 10.0
    world.ball.velocity = 0.0
    world.readings = world.sensor_readings()
    world.run_robot_headless(duration=0.1, dt=0.1)

    assert world.correct_grips == 1
    assert world.ball.caught
    assert world.touch_pressed


def test_consumed_prey_respawns_only_after_the_robot_opens() -> None:
    """An absent prey waits for a later opening transition before replacement."""
    config = replace(WORLD_CONFIG, consumption_time=0.1)
    world = GraspingWorld.demo(ClassicalGripper(), seed=5, config=config)
    world.ball.distance = 10.0
    world.ball.velocity = 0.0

    world.step(1.0, 0.1)
    world.step(1.0, 0.1)
    assert not world.ball.present

    # Continuing to command closed cannot create new prey behind the jaws.
    world.step(1.0, 0.1)
    assert not world.ball.present

    world.step(0.0, 0.1)
    assert world.ball.present
    assert not world.ball.caught
    assert world.ball.distance >= world.prey_config.respawn_distance_range[0]


def test_opening_before_consumption_releases_the_same_prey() -> None:
    """A premature opening records failure and lets the captured prey escape."""
    config = replace(WORLD_CONFIG, consumption_time=1.0)
    world = GraspingWorld.demo(ClassicalGripper(), seed=6, config=config)
    world.ball.distance = 10.0
    world.ball.velocity = 0.0

    world.step(1.0, 0.1)
    captured_prey = world.ball
    world.step(0.0, 0.1)

    assert world.ball is captured_prey
    assert world.ball.present
    assert not world.ball.caught
    assert world.ball.velocity >= world.prey_config.escape_speed
    assert world.premature_releases == 1
    assert world.consumed_prey == 0


def test_opening_at_consumption_completion_counts_as_successful() -> None:
    """A release at the completed chewing boundary is not premature."""
    world_config = replace(WORLD_CONFIG, consumption_time=0.3)
    world = GraspingWorld.demo(ClassicalGripper(), seed=7, config=world_config)
    world.ball.distance = 10.0
    world.ball.velocity = 0.0

    # Consumption is processed before a simultaneous opening transition. The
    # opening therefore respawns prey instead of being recorded as premature.
    world.step(1.0, 0.1)
    world.step(1.0, 0.2)
    world.step(0.0, 0.1)

    assert world.consumed_prey == 1
    assert world.premature_releases == 0
    assert not world.gripper.gripper_closed
    assert world.ball.present


def test_sensor_readings_use_the_world_configuration() -> None:
    """Per-trial sensing bounds replace defaults in the physical interface."""
    config = replace(WORLD_CONFIG, near_distance=10.0, far_distance=30.0)
    world = GraspingWorld.demo(ClassicalGripper(), seed=2, config=config)
    world.ball.distance = 20.0

    # Twenty centimetres is the midpoint only under the injected 10--30 cm
    # interval, which distinguishes this result from the default mapping.
    assert world.sensor_readings()["proximity"] == pytest.approx(0.5)


def test_world_distinguishes_empty_closures_from_missed_visits() -> None:
    """The two failure counters correspond to different physical events."""
    world = GraspingWorld.demo(ClassicalGripper(), seed=8)

    # Closing while the ball is far away is an empty grip.
    world.ball.distance = 30.0
    world.step(1.0, 0.01)
    assert world.empty_grips == 1

    # Reopen, let the ball enter the jaw interval, then move it out without a
    # second closing transition. That completed uncaught visit is a miss.
    world.step(0.0, 0.01)
    world.ball.distance = 10.0
    world.ball.velocity = 0.0
    world.step(0.0, 0.01)
    world.ball.distance = 16.0
    world.step(0.0, 0.01)

    assert world.missed_grips == 1


def test_demo_accepts_a_preconfigured_prey() -> None:
    """A caller can supply exact prey state instead of sampling a spawn."""
    prey_config = replace(BALL_PREY_CONFIG, max_near_duration=0.4)
    prey = BallPrey(0.0, 0.0, distance=17.0, velocity=-2.0, config=prey_config)

    # Identity is significant here: experiments may retain and inspect their
    # configured prey object before and after passing it to the world.
    world = GraspingWorld.demo(gripper=ClassicalGripper(), seed=9, prey=prey)

    assert world.ball is prey
    assert world.prey_config is prey_config
    assert world.ball.distance == 17.0
