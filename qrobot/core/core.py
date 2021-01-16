
import json
import multiprocessing
import os

from ..logs import get_logger
from .singleton import Singleton

ADDRESS = 'tcp://127.0.0.1'
PORT = 31313
CORE_PERIOD = 0.001


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
        
        # Store address
        self._address = f"{ADDRESS}:{PORT}"
        # Store global period
        self.T = CORE_PERIOD

        self._logger.info("Core initialized")

    @property
    def address(self) -> str:
        return self._address

    def __dict__(self) -> dict:
        return {
            k: v.__dict__()
            for k, v
            in self._qunits.items()
        }

    def __iter__(self):
        return iter([v for _, v in self._qunits.items()])

    def __getitem__(self, i):
        return [v for _, v in self._qunits.items()][i]

    def __repr__(self):
        repr = "Quantum-Robot Core\n"
        repr += json.dumps(self.__dict__(), indent=4, sort_keys=False)
        return repr

    def add_qunit(self, qunit) -> None:
        self._qunits[qunit.id] = qunit
        self._logger.info(f"Added QUnit \"{qunit.id}\"")

    def remove_qunit(self, qunit) -> None:
        self._qunits.pop(qunit.id)
        self._logger.info(f"Removed QUnit \"{qunit.id}\"")

    def qunit(self, id):
        return self._qunits[id]
