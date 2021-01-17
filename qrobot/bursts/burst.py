from abc import ABC, abstractmethod


class Burst(ABC):
    """Parent abstract class of all bursts. Every burst sould work
    by being called and returning a ``float`` (the burst value)."""

    @ abstractmethod
    def __call__(self, state: str) -> float:
        pass
