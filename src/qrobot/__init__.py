"""Core quantum-like perception models and burst strategies.

Optional integrations live in separate import packages in the same distribution.
Install their dependencies with the corresponding ``quantum-robot`` extras.
"""

from . import bursts, logger, models

__all__ = [
    "bursts",
    "logger",
    "models",
]
