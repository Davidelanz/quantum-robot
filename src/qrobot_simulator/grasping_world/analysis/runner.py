"""Recorded execution of one controlled grasping encounter."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from .recording import (
    GraspingEvent,
    GraspingRunMetadata,
    GraspingRunRecord,
    capture_sample,
    summarize_encounter,
)

if TYPE_CHECKING:
    from .controlled_world import ControlledGraspingWorld


@dataclass(frozen=True)
class _EventState:
    """Retain the world values needed to recognize changes after one step."""

    gripper_closed: bool
    correct_grips: int
    empty_grips: int
    consumed_prey: int
    premature_releases: int


def record_encounter(
    world: ControlledGraspingWorld,
    duration: float,
    dt: float,
) -> GraspingRunRecord:
    """Run one predefined ball visit and retain its inputs, actions, and events."""
    if duration <= 0 or dt <= 0:
        raise ValueError("duration and dt must be positive")

    samples = [capture_sample(world, activation=0.0)]
    events: list[GraspingEvent] = []
    world.gripper.prepare_headless(world.readings)
    try:
        target = world.elapsed + duration
        while world.elapsed < target:
            step_dt = min(dt, target - world.elapsed)
            before = _event_state(world)
            activation = world.gripper.command(world.readings.copy(), step_dt)
            world.step(activation, step_dt)
            events.extend(_events_after_step(world, before))
            samples.append(capture_sample(world, activation))
    finally:
        world.gripper.stop()

    metadata = GraspingRunMetadata(
        encounter=world.encounter,
        world_config=world.config,
        prey_config=world.prey_config,
        gripper_config=world.gripper.config,
        seed=world.seed,
        disturbance_seed=world.disturbance_seed,
        duration=duration,
        physics_step=dt,
    )
    immutable_events = tuple(events)
    return GraspingRunRecord(
        samples=tuple(samples),
        events=immutable_events,
        metadata=metadata,
        outcome=summarize_encounter(immutable_events, world.encounter),
    )


def _event_state(world: ControlledGraspingWorld) -> _EventState:
    """Copy the cumulative values used to recognize events after a step."""
    return _EventState(
        gripper_closed=world.gripper.gripper_closed,
        correct_grips=world.correct_grips,
        empty_grips=world.empty_grips,
        consumed_prey=world.consumed_prey,
        premature_releases=world.premature_releases,
    )


def _events_after_step(world: ControlledGraspingWorld, before: _EventState) -> list[GraspingEvent]:
    """Describe physical changes caused by the most recent brain command."""
    elapsed = world.elapsed
    events: list[GraspingEvent] = []
    if not before.gripper_closed and world.gripper.gripper_closed:
        events.append(GraspingEvent(elapsed, "jaws_closed"))
    events.extend(
        GraspingEvent(elapsed, "prey_captured")
        for _ in range(world.correct_grips - before.correct_grips)
    )
    events.extend(
        GraspingEvent(elapsed, "empty_closure")
        for _ in range(world.empty_grips - before.empty_grips)
    )
    events.extend(
        GraspingEvent(elapsed, "prey_consumed")
        for _ in range(world.consumed_prey - before.consumed_prey)
    )
    events.extend(
        GraspingEvent(elapsed, "premature_release")
        for _ in range(world.premature_releases - before.premature_releases)
    )
    if before.gripper_closed and not world.gripper.gripper_closed:
        events.append(GraspingEvent(elapsed, "jaws_opened"))
    return events
