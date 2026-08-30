"""Burst strategies for converting measured states to scalar signals."""

from .burst import Burst
from .oneburst import OneBurst
from .zeroburst import ZeroBurst

__all__ = ["Burst", "ZeroBurst", "OneBurst"]
