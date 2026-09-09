"""Controlled grasping encounters used by external experiment runners."""

from dataclasses import replace

import pytest

from qrobot_simulator.grasping_world import ClassicalGripper
from qrobot_simulator.grasping_world.analysis import (
    ControlledGraspingWorld,
    GraspingEncounter,
    MotionSegment,
    ProximityDisturbance,
    TimeInterval,
)
from qrobot_simulator.grasping_world.world.config import WORLD_CONFIG


def test_scripted_motion_gives_same_position_with_large_or_small_steps() -> None:
    """Physics-step size does not change the ball's prescribed movement."""
    encounter = GraspingEncounter(
        initial_distance=18.0,
        motion=(MotionSegment(0.25, -4.0), MotionSegment(0.25, 2.0)),
        opportunity=TimeInterval(0.1, 0.3),
    )
    single_step = ControlledGraspingWorld.create(ClassicalGripper(), encounter, seed=12)
    split_steps = ControlledGraspingWorld.create(ClassicalGripper(), encounter, seed=12)

    # The 0.5 s step crosses the velocity change. The controlled integrator must
    # apply each segment only for its specified duration rather than using the
    # first velocity for the whole physics interval.
    single_step.step(0.0, 0.5)
    split_steps.step(0.0, 0.25)
    split_steps.step(0.0, 0.25)

    assert single_step.ball.distance == pytest.approx(17.5)
    assert split_steps.ball.distance == pytest.approx(single_step.ball.distance)
    assert encounter.is_valid_opportunity(0.1)
    assert not encounter.is_valid_opportunity(0.4)


def test_reading_a_sensor_extra_times_does_not_change_later_noise() -> None:
    """Inspecting a sensor does not change the later values it will produce."""
    encounter = GraspingEncounter(
        initial_distance=12.5,
        motion=(MotionSegment(1.0, 0.0),),
        opportunity=TimeInterval(0.0, 1.0),
        disturbance=ProximityDisturbance(noise_standard_deviation=0.1),
    )
    world_with_extra_reads = ControlledGraspingWorld.create(ClassicalGripper(), encounter, seed=41)
    world_without_extra_reads = ControlledGraspingWorld.create(
        ClassicalGripper(), encounter, seed=41
    )

    initial = world_with_extra_reads.sensor_readings()["proximity"]
    assert world_with_extra_reads.sensor_readings()["proximity"] == initial
    assert world_without_extra_reads.sensor_readings()["proximity"] == initial

    # Extra reads above do not advance a generator, so both worlds still expose
    # the same disturbed value after their state advances to the next instant.
    world_with_extra_reads.step(0.0, 0.1)
    world_without_extra_reads.step(0.0, 0.1)
    assert (
        world_with_extra_reads.readings["proximity"]
        == world_without_extra_reads.readings["proximity"]
    )


def test_dropout_reports_zero_and_false_detection_reports_one() -> None:
    """Each configured sensor error produces its stated proximity value."""
    encounter = GraspingEncounter(
        initial_distance=12.5,
        motion=(MotionSegment(0.6, 0.0),),
        opportunity=None,
        disturbance=ProximityDisturbance(
            dropouts=(TimeInterval(0.0, 0.2),),
            false_positives=(TimeInterval(0.2, 0.2),),
        ),
    )
    world = ControlledGraspingWorld.create(ClassicalGripper(), encounter, seed=9)

    assert world.readings["proximity"] == 0.0
    world.step(0.0, 0.2)
    assert world.readings["proximity"] == 1.0
    world.step(0.0, 0.2)
    assert world.readings["proximity"] == pytest.approx(0.5)


def test_random_sensor_noise_requires_a_seed() -> None:
    """Random sensor noise cannot silently become unreproducible or inactive."""
    encounter = GraspingEncounter(
        initial_distance=12.5,
        motion=(MotionSegment(1.0, 0.0),),
        opportunity=None,
        disturbance=ProximityDisturbance(noise_standard_deviation=0.1),
    )

    with pytest.raises(ValueError, match="seed is required"):
        ControlledGraspingWorld.create(ClassicalGripper(), encounter)


def test_consumed_ball_does_not_respawn_during_a_controlled_visit() -> None:
    """Opening completes the predefined visit without introducing a new ball."""
    encounter = GraspingEncounter(
        initial_distance=10.0,
        motion=(MotionSegment(1.0, 0.0),),
        opportunity=TimeInterval(0.0, 0.5),
    )
    world = ControlledGraspingWorld.create(
        ClassicalGripper(),
        encounter,
        config=replace(WORLD_CONFIG, consumption_time=0.1),
    )

    world.step(1.0, 0.1)
    world.step(1.0, 0.1)
    world.step(0.0, 0.1)

    assert not world.ball.present
