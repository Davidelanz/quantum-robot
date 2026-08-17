"""Core quantum-like perception models and burst strategies.

Optional integrations live in separately installable distributions:
``qrobot-qunits``, ``qrobot-visualization``, and ``qrobot-dashboard``.
"""

from . import bursts, logger, models

__all__ = [
    "bursts",
    "logger",
    "models",
]
