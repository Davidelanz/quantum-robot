import ctypes
import multiprocessing
from time import sleep
from uuid import uuid4

from ..core import Core
from ..bursts import Burst
from ..logs import get_logger
from ..models import Model


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
        self._burst = burst
        self.n = model.n
        self.tau = model.tau
        self.Ts = Ts

        if query is None:
            query = [.0]*(self.n)

        # Initialize multiprocessing variables (common to all threads while
        # being modified)
        manager = multiprocessing.Manager()

        self._query = manager.Array('d', query)
        # Initialize input data accumulator
        self._in_data = manager.Array('d', [.0]*(self.n))
        # Initialize output accumulators
        self._out_state = manager.Value(ctypes.c_char_p, "")
        self._out_burst = manager.Value('d', 0)

        # Initialize thread
        self._process = None

        # Log properties
        self._logger.debug(f"Properties: {self}")

    def __repr__(self) -> str:
        return f"QUnit \"{self.name}\" | name={self.name} | n={self.n} | " +\
            f"tau={self.tau} | Ts={self.Ts} | query={self._query}"
    
    def __dict__(self) -> str:
        return {
            "name" : self.name, 
            "n" : self.n,
            "tau" : self.tau,
            "Ts" : self.Ts
        }

    def query(self, query) -> str:
        self._logger.debug(f"Changing query from {self._query} to {query}")
        for i, q in enumerate(query):
            self._query[i] = q
        self._logger.debug(f"_query={self._query}")

    def input(self, scalar_input, dim) -> None:
        self._logger.debug(f"Input {scalar_input} on dim={dim}")
        self._in_data[dim] = scalar_input
        self._logger.debug(f"_in_data={self._in_data}")

    def burst(self) -> float: return self._out_burst.value

    def start(self) -> None:
        """Loads qunit on the Core"""
        self._logger.debug(f"Loading qUnit on Core")
        Core().add_qunit(self)
        self._logger.info(f"Starting qUnit")
        self._process = multiprocessing.Process(target=self.__loop)
        self._process.start()

    def stop(self) -> None:
        """Stops the qUnit background thread"""
        if self._process is None:
            self._logger.warning("qUnit is already stopped")
        else:
            self._logger.info("Stopping qUnit")
            self._process.terminate()
            Core().remove_qunit(self)

    def __loop(self) -> None:
        while True:
            self._logger.debug(f"Initializing a new temporal window")
            self.model.clear()
            # Encode events in the time window
            for t in range(self.model.tau):
                self._logger.debug(
                    f"Temporal window event {t+1}/{self.model.tau}")
                # Loop through the dimensions to encode data
                for dim in range(self.model.n):
                    self._logger.debug(f"Encoding {self._in_data[dim]} " +
                                       f"in dimension {dim}")
                    self.model.encode(self._in_data[dim], dim)
                # wait for the next input in the time window
                sleep(self.Ts)
            # After the time window, apply the query
            self._logger.debug(f"Querying for state {self._query}")
            self.model.query(self._query)
            # Store decoding in accumulators
            self._out_state.value = self.model.decode()
            self._logger.debug(f"Decoded state: {self._out_state.value}")
            self._out_burst.value = self._burst(self._out_state.value)
            self._logger.debug(f"Burst: {self._out_burst.value}")
