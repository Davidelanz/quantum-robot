"""Controlled form of the grasping world used for analytical comparisons."""

from __future__ import annotations

from random import Random

from ..robots.ball_prey import BallPrey
from ..robots.base_gripper import BaseGripper
from ..robots.config import BALL_PREY_CONFIG, BallPreyConfig
from ..world.arena import GraspingArena
from ..world.config import WORLD_CONFIG, GraspingWorldConfig
from ..world.grasping_world import GraspingWorld
from .encounter import GraspingEncounter


class ControlledGraspingWorld(GraspingWorld):
    """Present one predefined ball visit instead of randomly wandering prey.

    This class uses the sensors and physical interactions of `GraspingWorld`, but
    the analysis code supplies the ball's starting distance, movement, and optional
    sensor errors. Consumed prey does not respawn because each instance represents
    one visit. The random demonstration remains entirely in `GraspingWorld`.
    """

    encounter: GraspingEncounter
    disturbance_seed: int | None

    @classmethod
    def create(
        cls,
        gripper: BaseGripper,
        encounter: GraspingEncounter,
        seed: int | None = None,
        disturbance_seed: int | None = None,
        config: GraspingWorldConfig = WORLD_CONFIG,
        prey_config: BallPreyConfig = BALL_PREY_CONFIG,
    ) -> ControlledGraspingWorld:
        """Create one repeatable visit for a classical or quantum gripper."""
        if encounter.initial_distance > prey_config.max_distance:
            raise ValueError("encounter initial distance exceeds the prey limit")
        if any(abs(segment.velocity) > prey_config.max_speed for segment in encounter.motion):
            raise ValueError("encounter velocity exceeds the prey speed limit")
        selected_disturbance_seed = seed if disturbance_seed is None else disturbance_seed
        if encounter.disturbance.noise_standard_deviation > 0 and selected_disturbance_seed is None:
            raise ValueError("a seed is required when an encounter adds random noise")

        rng = Random(seed)
        ball = BallPrey(
            0.0,
            gripper.y,
            encounter.initial_distance,
            encounter.velocity_at(0.0),
            config=prey_config,
        )
        world = cls(
            arena=GraspingArena(
                config.arena_width,
                config.arena_height,
                config.arena_cell_size,
            ),
            gripper=gripper,
            ball=ball,
            config=config,
            prey_config=prey_config,
            seed=seed,
            _rng=rng,
        )
        world.encounter = encounter
        world.disturbance_seed = selected_disturbance_seed
        world._update_ball_position()
        world.readings = world.sensor_readings()
        return world

    def sensor_readings(self) -> dict[str, float]:
        """Return normal world readings with the configured sensor errors added."""
        readings = super().sensor_readings()
        readings["proximity"] = self.encounter.disturbance.apply(
            readings["proximity"],
            self.elapsed,
            self.disturbance_seed,
        )
        return readings

    def _advance_ball(self, dt: float) -> None:
        """Move free prey through the prescribed constant-velocity segments."""
        if self.ball.caught:
            self.ball.velocity = 0.0
            return
        if not self.ball.present:
            return

        closed_barrier = self.config.grippable_distance if self.gripper.gripper_closed else None
        start = max(0.0, self.elapsed - dt)
        remaining = dt
        while remaining > 0:
            self.ball.velocity = self.encounter.velocity_at(start)
            boundary = self.encounter.next_motion_boundary(start)
            interval = min(remaining, max(0.0, boundary - start))
            if interval == 0:
                self.ball.velocity = 0.0
                break
            self.ball.advance(interval, self.config.minimum_distance, closed_barrier)
            start += interval
            remaining -= interval

    def _respawn_ball(self) -> None:
        """Complete the single visit without introducing another random ball."""
        self.ball.caught = False
        self._consumption_started_at = None
