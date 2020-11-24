
import json
import multiprocessing
import os

from ..logs import get_logger
from .singleton import Singleton


class Core(object, metaclass=Singleton):
    """
    Central Core to manage all QUnit instances.
    Singleton implementation prevents from creating more than one instance.
    """

    def __init__(self) -> None:
        # Initialize logger
        self._logger = get_logger("core")
        # Initialize qunits dictionary
        self._qunits = {}

        self._logger.info("Core initialized")

    def __dict__(self) -> dict:
        return {
            k: v.__dict__()
            for k, v
            in self._qunits.items()
        }

    def __repr__(self):
        repr = "Quantum-Robot Core\n"
        repr += json.dumps(self.__dict__(), indent=4, sort_keys=False)
        return repr

    def add_qunit(self, qunit) -> None:
        self._qunits[qunit.id] = qunit
        self._logger.info(f"Added QUnit {qunit}")

    def remove_qunit(self, qunit) -> None:
        self._qunits.pop(qunit.id)
        self._logger.info(f"Removed QUnit {qunit}")

    def qunit(self, id):
        return self._qunits[id]

