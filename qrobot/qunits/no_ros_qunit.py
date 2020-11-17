from os import name
from threading import Thread
from uuid import uuid4  # unique identifier generator

import rospy
from std_msgs.msg import Float32, String

from ..bursts import Burst
from ..logs import get_logger
from ..models import Model
from ..core import Core


class QUnit():
    """ [QUnit]

    Attributes
    ----------
    id : str
        The unique instance identifier of the qUnit
    model : qrobot.Model
        The model which the qUnit implements
    n : int
        The model dimension
    tau : int
        The number of events in the qUnit's temporal window
    Ts : float
        The sampling period for which the qUnit samples an event
    query : list
        If present, contains the target state for the model queries
    """

    def __init__(self, name: str, model: Model, burst: Burst,
                 Ts: float, query: list = None) -> None:
        """[__init__]

        Args:
            name (str): The qUnit name
            model (qrobot.models.Model): The model the qUnit implements
            model (qrobot.bursts.Burst): The burst the qUnit implements
            Ts (float): The sampling time with wich the qUnit reads the input
            query (list): The target state for the model queries. Defaults to None

        """
        # Create a instance unique identifier
        self.id = name + "_" + str(uuid4())
        # use it for log
        self._logger = get_logger(self.id)
        self._logger.debug(f"Initializing qUnit {self.id}")

        # Store the qUnits name and properties
        self.name = name
        self.model = model
        self.burst = burst
        self.n = model.n
        self.tau = model.tau
        self.Ts = Ts
        self.query = query
        self._logger.debug(f"qUnit properties: name={self.name} - " +
                           f"n={self.n} - tau={self.tau} - Ts={self.Ts} - " +
                           f"query={self.query}")

        # Initialize input data accumulator
        self._in_data = [.0]*self.n

    def load(self) -> None:
        """Loads qunit on the Core"""
        self._logger.debug(f"Loading qUnit on Core")
        core = Core()
        core.add_qunit(self)

    def start(self) -> None:
        """Starts the Core (if not already running)"""
        core = Core()
        core.start()

    def __repr__(self) -> str:
        return f"""QUnit \"{self.name}\"
    name={self.name}
    n={self.n}
    tau={self.tau}
    Ts={self.Ts}
    query={self.query}
    """