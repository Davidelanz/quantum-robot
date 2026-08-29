from abc import ABC, abstractmethod


class Burst(ABC):
    """Callable interface for converting a measured state to a scalar signal."""

    @abstractmethod
    def __call__(self, state: str) -> float:
        """Return the burst value for ``state``."""
        raise NotImplementedError
