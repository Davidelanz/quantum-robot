"""Structured raw observations produced by headless bug-world runs."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal, TypeAlias

from ..robots.base_robot import Robot

if TYPE_CHECKING:
    from .bug_world import BugWorld

EventKind: TypeAlias = Literal["prey_bite", "predator_bite", "boundary_crossing"]


@dataclass(frozen=True)
class RobotPose:
    """Store one robot pose without retaining its mutable body.

    :param name: Stable robot name.
    :param x: Horizontal world coordinate.
    :param y: Vertical world coordinate.
    :param heading: Orientation in radians.
    """

    name: str
    x: float
    y: float
    heading: float


@dataclass(frozen=True)
class BugWorldSample:
    """Store world, sensor, controller, and distance values at one step.

    :param elapsed: Simulated seconds elapsed.
    :param bug: Controlled bug pose.
    :param prey: Poses of all prey.
    :param predator: Predator pose.
    :param readings: Normalized sensor readings.
    :param diagnostics: Values exposed by the selected brain.
    :param behavior: Current behavior label.
    :param bitten_prey: Cumulative successful prey bites.
    :param predator_bites: Cumulative predator contacts.
    :param boundary_crossings: Cumulative crossings keyed by robot name.
    :param nearest_prey_distance: Distance to the nearest prey.
    :param predator_distance: Distance to the predator.
    """

    elapsed: float
    bug: RobotPose
    prey: tuple[RobotPose, ...]
    predator: RobotPose
    readings: dict[str, float]
    diagnostics: dict[str, float | None]
    behavior: str
    bitten_prey: int
    predator_bites: int
    boundary_crossings: dict[str, int]
    nearest_prey_distance: float
    predator_distance: float


@dataclass(frozen=True)
class BugWorldEvent:
    """Record a discrete interaction or arena-boundary event.

    :param elapsed: Simulated event time in seconds.
    :param kind: Prey bite, predator bite, or boundary crossing.
    :param subject: Name of the robot responsible for the event.
    """

    elapsed: float
    kind: EventKind
    subject: str


@dataclass(frozen=True)
class BugRunRecord:
    """Collect samples, events, and behavior occupancy.

    :param samples: Immutable time-ordered world samples.
    :param events: Immutable time-ordered discrete events.
    :param behaviors: Number of steps spent in each behavior.
    """

    samples: tuple[BugWorldSample, ...]
    events: tuple[BugWorldEvent, ...]
    behaviors: Counter[str]


def capture_sample(world: BugWorld) -> BugWorldSample:
    """Copy the current world state into one immutable raw sample."""

    def pose(robot: Robot) -> RobotPose:
        """Copy the mutable robot coordinates into a recorded pose."""
        return RobotPose(robot.name, robot.x, robot.y, robot.heading)

    return BugWorldSample(
        elapsed=world.elapsed,
        bug=pose(world.bug),
        prey=tuple(pose(prey) for prey in world.prey),
        predator=pose(world.predator),
        readings=world.readings.copy(),
        diagnostics=world.bug.diagnostics(),
        behavior=world.bug.behavior or "IDLE",
        bitten_prey=world.bitten_prey,
        predator_bites=world.predator_bites,
        boundary_crossings=dict(world.boundary_crossings),
        nearest_prey_distance=min(
            (world.bug.distance_to(prey) for prey in world.prey),
            default=float("inf"),
        ),
        predator_distance=world.bug.distance_to(world.predator),
    )


def new_events(
    world: BugWorld,
    previous_prey_bites: int,
    previous_predator_bites: int,
    previous_crossings: Counter[str],
) -> list[BugWorldEvent]:
    """Describe changes in cumulative interaction counters after one step."""
    events = [
        BugWorldEvent(world.elapsed, "prey_bite", world.bug.name)
        for _ in range(world.bitten_prey - previous_prey_bites)
    ]
    events.extend(
        BugWorldEvent(world.elapsed, "predator_bite", world.predator.name)
        for _ in range(world.predator_bites - previous_predator_bites)
    )
    for name, total in world.boundary_crossings.items():
        events.extend(
            BugWorldEvent(world.elapsed, "boundary_crossing", name)
            for _ in range(total - previous_crossings[name])
        )
    return events
