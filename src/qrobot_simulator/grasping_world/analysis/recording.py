"""Raw observations, physical events, and results from one grasping encounter."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal, TypeAlias

from ..robots.config import BaseGripperConfig, BallPreyConfig
from ..world.config import GraspingWorldConfig
from .encounter import GraspingEncounter

if TYPE_CHECKING:
    from .controlled_world import ControlledGraspingWorld

EventKind: TypeAlias = Literal[
    "jaws_closed",
    "prey_captured",
    "empty_closure",
    "prey_consumed",
    "jaws_opened",
    "premature_release",
]
OutcomeLabel: TypeAlias = Literal[
    "true_positive",
    "false_positive",
    "false_negative",
    "correct_rejection",
]


@dataclass(frozen=True)
class GraspingSample:
    """Store everything needed to inspect one instant of the simulation.

    The sample contains the readings available to the brain, its returned jaw
    command, and the physical state after that command has been applied.
    """

    elapsed: float
    ball_distance: float
    ball_velocity: float
    ball_present: bool
    ball_caught: bool
    gripper_closed: bool
    activation: float
    proximity: float
    touch: float
    valid_opportunity: bool
    diagnostics: dict[str, float | None]


@dataclass(frozen=True)
class GraspingEvent:
    """Record one discrete physical action or consequence and when it occurred."""

    elapsed: float
    kind: EventKind


@dataclass(frozen=True)
class GraspingRunMetadata:
    """Identify the complete setup required to repeat one recorded run."""

    encounter: GraspingEncounter
    world_config: GraspingWorldConfig
    prey_config: BallPreyConfig
    gripper_config: BaseGripperConfig
    seed: int | None
    disturbance_seed: int | None
    duration: float
    physics_step: float


@dataclass(frozen=True)
class GraspingOutcome:
    """Summarize whether the robot acted correctly during one encounter.

    A valid encounter is a true positive when prey is captured during the
    declared opportunity and a false negative otherwise. An encounter without
    an opportunity is a false positive when the robot closes its jaws and a
    correct rejection when it leaves them open.

    Capture latency measures the delay from the start of a valid opportunity to
    capture. Release latency measures the delay from consumption to the first
    subsequent opening. ``failed_release`` is true when consumed prey disappears
    but the robot is still closed when recording ends.
    """

    label: OutcomeLabel
    capture_latency: float | None
    release_latency: float | None
    premature_releases: int
    extra_closures: int
    failed_release: bool


@dataclass(frozen=True)
class GraspingRunRecord:
    """Collect raw samples, events, setup metadata, and the derived result."""

    samples: tuple[GraspingSample, ...]
    events: tuple[GraspingEvent, ...]
    metadata: GraspingRunMetadata
    outcome: GraspingOutcome


def capture_sample(world: ControlledGraspingWorld, activation: float) -> GraspingSample:
    """Copy the current mutable world into an immutable raw sample."""
    opportunity = world.encounter.opportunity
    return GraspingSample(
        elapsed=world.elapsed,
        ball_distance=world.ball.distance,
        ball_velocity=world.ball.velocity,
        ball_present=world.ball.present,
        ball_caught=world.ball.caught,
        gripper_closed=world.gripper.gripper_closed,
        activation=activation,
        proximity=world.readings["proximity"],
        touch=world.readings["touch"],
        valid_opportunity=opportunity is not None and opportunity.contains(world.elapsed),
        diagnostics=world.gripper.diagnostics(),
    )


def summarize_encounter(
    events: tuple[GraspingEvent, ...],
    encounter: GraspingEncounter,
) -> GraspingOutcome:
    """Derive classification and response times from recorded physical events."""
    closures = [event for event in events if event.kind == "jaws_closed"]
    captures = [event for event in events if event.kind == "prey_captured"]
    opportunity = encounter.opportunity

    valid_capture = next(
        (
            event
            for event in captures
            if opportunity is not None and opportunity.contains(event.elapsed)
        ),
        None,
    )
    if opportunity is None:
        label: OutcomeLabel = "false_positive" if closures else "correct_rejection"
    else:
        label = "true_positive" if valid_capture is not None else "false_negative"

    consumption = next((event for event in events if event.kind == "prey_consumed"), None)
    opening_after_consumption = next(
        (
            event
            for event in events
            if event.kind == "jaws_opened"
            and consumption is not None
            and event.elapsed >= consumption.elapsed
        ),
        None,
    )
    return GraspingOutcome(
        label=label,
        capture_latency=(
            valid_capture.elapsed - opportunity.start
            if valid_capture is not None and opportunity is not None
            else None
        ),
        release_latency=(
            opening_after_consumption.elapsed - consumption.elapsed
            if opening_after_consumption is not None and consumption is not None
            else None
        ),
        premature_releases=sum(event.kind == "premature_release" for event in events),
        extra_closures=max(0, len(closures) - 1),
        failed_release=consumption is not None and opening_after_consumption is None,
    )
