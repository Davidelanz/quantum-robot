"""Headless execution loops shared by bug-world controllers."""

from __future__ import annotations

from collections import Counter
from collections.abc import Callable
from typing import TYPE_CHECKING

from .recording import BugRunRecord, capture_sample, new_events

if TYPE_CHECKING:
    from .bug_world import BugWorld

Controller = Callable[[dict[str, float]], dict[str, float]]


def run_controller(
    world: BugWorld,
    controller: Controller,
    duration: float,
    dt: float,
) -> Counter[str]:
    """Advance an external controller and count displayed behaviors."""
    _validate_run(duration, dt)
    target = world.elapsed + duration
    behaviors: Counter[str] = Counter()
    while world.elapsed < target:
        world.step(controller(world.readings.copy()), min(dt, target - world.elapsed))
        behaviors[world.bug.behavior or "IDLE"] += 1
    return behaviors


def run_brain(world: BugWorld, duration: float, dt: float) -> Counter[str]:
    """Run the world's configured brain through the common bug interface."""
    _validate_run(duration, dt)
    world.bug.start(world.readings)
    try:
        target = world.elapsed + duration
        behaviors: Counter[str] = Counter()
        while world.elapsed < target:
            step_dt = min(dt, target - world.elapsed)
            world.step(world.bug.command(world.readings.copy(), step_dt), step_dt)
            behaviors[world.bug.behavior or "IDLE"] += 1
        return behaviors
    finally:
        world.bug.stop()


def run_recorded_brain(world: BugWorld, duration: float, dt: float) -> BugRunRecord:
    """Run the configured brain and retain raw samples and discrete events."""
    _validate_run(duration, dt)
    samples = []
    events = []
    behaviors: Counter[str] = Counter()
    previous_prey_bites = world.bitten_prey
    previous_predator_bites = world.predator_bites
    previous_crossings = world.boundary_crossings.copy()
    world.bug.start(world.readings)
    try:
        target = world.elapsed + duration
        while world.elapsed < target:
            step_dt = min(dt, target - world.elapsed)
            world.step(world.bug.command(world.readings.copy(), step_dt), step_dt)
            behaviors[world.bug.behavior or "IDLE"] += 1
            samples.append(capture_sample(world))
            events.extend(
                new_events(
                    world,
                    previous_prey_bites,
                    previous_predator_bites,
                    previous_crossings,
                )
            )
            previous_prey_bites = world.bitten_prey
            previous_predator_bites = world.predator_bites
            previous_crossings = world.boundary_crossings.copy()
    finally:
        world.bug.stop()
    return BugRunRecord(tuple(samples), tuple(events), behaviors)


def _validate_run(duration: float, dt: float) -> None:
    """Reject empty or backwards simulated intervals."""
    if duration <= 0 or dt <= 0:
        raise ValueError("duration and dt must be positive")
