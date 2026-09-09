"""Recorded evidence and results from one controlled ball visit."""

from dataclasses import replace

import pytest

from qrobot_simulator.grasping_world import ReactiveGripper
from qrobot_simulator.grasping_world.analysis import (
    ControlledGraspingWorld,
    GraspingEncounter,
    GraspingEvent,
    MotionSegment,
    TimeInterval,
    record_encounter,
    summarize_encounter,
)
from qrobot_simulator.grasping_world.world.config import WORLD_CONFIG


def test_recorded_run_keeps_initial_state_every_step_and_physical_events() -> None:
    """A short successful visit retains the evidence behind its final result."""
    encounter = GraspingEncounter(
        initial_distance=10.0,
        motion=(MotionSegment(1.0, 0.0),),
        opportunity=TimeInterval(0.0, 0.5),
    )
    world = ControlledGraspingWorld.create(
        ReactiveGripper(),
        encounter,
        seed=21,
        disturbance_seed=22,
        config=replace(WORLD_CONFIG, consumption_time=0.09),
    )

    record = record_encounter(world, duration=0.3, dt=0.1)

    # The initial sample plus three simulation steps show exactly what the brain
    # received and what happened after each returned command.
    assert len(record.samples) == 4
    assert record.samples[0].elapsed == 0.0
    assert record.samples[1].activation == 1.0
    assert [event.kind for event in record.events] == [
        "jaws_closed",
        "prey_captured",
        "prey_consumed",
        "jaws_opened",
    ]
    assert record.outcome.label == "true_positive"
    assert record.outcome.capture_latency == pytest.approx(0.1)
    assert record.outcome.release_latency == pytest.approx(0.1)
    assert not record.outcome.failed_release

    # Seeds and frozen setup objects travel with the observations so the
    # experiment repository can save a complete description of this run.
    assert record.metadata.encounter is encounter
    assert record.metadata.seed == 21
    assert record.metadata.disturbance_seed == 22
    assert record.metadata.physics_step == 0.1


@pytest.mark.parametrize(
    ("opportunity", "events", "expected_label"),
    [
        (TimeInterval(1.0, 1.0), (), "false_negative"),
        (None, (GraspingEvent(1.0, "jaws_closed"),), "false_positive"),
        (None, (), "correct_rejection"),
    ],
)
def test_result_names_missed_valid_visits_and_responses_to_invalid_visits(
    opportunity: TimeInterval | None,
    events: tuple[GraspingEvent, ...],
    expected_label: str,
) -> None:
    """The four result names follow whether an opportunity and response exist."""
    encounter = GraspingEncounter(
        initial_distance=20.0,
        motion=(MotionSegment(3.0, 0.0),),
        opportunity=opportunity,
    )

    assert summarize_encounter(events, encounter).label == expected_label


def test_result_measures_capture_and_opening_delays_from_event_times() -> None:
    """Latency values are differences between their corresponding events."""
    encounter = GraspingEncounter(
        initial_distance=20.0,
        motion=(MotionSegment(6.0, 0.0),),
        opportunity=TimeInterval(1.0, 2.0),
    )
    events = (
        GraspingEvent(1.4, "jaws_closed"),
        GraspingEvent(1.4, "prey_captured"),
        GraspingEvent(4.0, "prey_consumed"),
        GraspingEvent(4.7, "jaws_opened"),
    )

    outcome = summarize_encounter(events, encounter)

    assert outcome.label == "true_positive"
    assert outcome.capture_latency == pytest.approx(0.4)
    assert outcome.release_latency == pytest.approx(0.7)


def test_result_reports_repeated_closing_early_release_and_failure_to_reopen() -> None:
    """Secondary failures remain visible alongside the primary classification."""
    encounter = GraspingEncounter(
        initial_distance=20.0,
        motion=(MotionSegment(6.0, 0.0),),
        opportunity=TimeInterval(1.0, 2.0),
    )
    events = (
        GraspingEvent(1.2, "jaws_closed"),
        GraspingEvent(1.2, "prey_captured"),
        GraspingEvent(1.8, "premature_release"),
        GraspingEvent(2.0, "jaws_closed"),
        GraspingEvent(4.5, "prey_consumed"),
    )

    outcome = summarize_encounter(events, encounter)

    assert outcome.premature_releases == 1
    assert outcome.extra_closures == 1
    assert outcome.failed_release
    assert outcome.release_latency is None
