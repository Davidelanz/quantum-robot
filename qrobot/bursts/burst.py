from abc import ABC, abstractmethod


class Burst(ABC):

    @ abstractmethod
    def __call__(self, state: str) -> float:
        """Every burst sould work by being called and returning a float."""