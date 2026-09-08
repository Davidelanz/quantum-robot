"""Configured construction of autonomous bug-world animals."""

from random import Random

from ..robots.blue_prey import BluePrey
from ..robots.config import PredatorConfig, PreyConfig
from ..robots.red_predator import RedPredator
from .config import WorldConfig


def create_prey(
    world_config: WorldConfig,
    prey_config: PreyConfig,
    rng: Random,
) -> list[BluePrey]:
    """Create each configured prey with an independent random generator."""
    return [
        BluePrey(
            name,
            x,
            y,
            heading,
            prey_config.color,
            motion_mode=motion_mode,
            config=prey_config,
            rng=Random(rng.randrange(2**32)),
        )
        for name, x, y, heading, motion_mode in world_config.prey_spawns
    ]


def create_predator(
    world_config: WorldConfig,
    predator_config: PredatorConfig,
    rng: Random,
) -> RedPredator:
    """Create the configured ideal predator with its own random generator."""
    return RedPredator(
        *world_config.predator_spawn,
        predator_config.color,
        max_speed=predator_config.max_speed,
        bite_period=predator_config.bite_period,
        config=predator_config,
        rng=Random(rng.randrange(2**32)),
    )
