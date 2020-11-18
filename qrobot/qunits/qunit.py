import multiprocessing
from uuid import uuid4
import ctypes

from matplotlib.pyplot import sca  # unique identifier generator

from ..bursts import Burst
from ..core import Core
from ..logs import get_logger
from ..models import Model
from time import sleep


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

        if query is None:
            query = [.0]*(self.n)

        # https://stackoverflow.com/questions/21290960/how-to-share-a-string-amongst-multiple-processes-using-managers-in-python
        #
        # Initialize multiprocessing variables (common to all threads while
        # being modified)
        manager = multiprocessing.Manager()

        self.query = manager.Array('d', query)
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
            f"tau={self.tau} | Ts={self.Ts} | query={self.query}"

    def input(self, scalar_input, dim) -> None:
        self._logger.debug(f"Input {scalar_input} on dim={dim}")
        self._in_data[dim] = scalar_input
        self._logger.debug(f"_in_data={self._in_data}")

    def burst(self) -> float: return self._out_burst

    def start(self) -> None:
        """Loads qunit on the Core"""
        self._logger.debug(f"Loading qUnit on Core")
        core = Core()
        core.add_qunit(self)
        core.start()

        self._logger.debug(f"Starting qUnit")
        self._process = multiprocessing.Process(target=self.__loop)
        self._process.start()

    def stop(self) -> None:
        """Stops the qUnit background thread"""
        if self._process is None:
            self._logger.warning(
                "Trying to stop qUnit, but qUnit is not running")
        else:
            self._logger.info("Stopping qUnit process")
            self._process.terminate()

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
            if self.query is not None:
                self._logger.debug(f"Querying for state {self.query}")
                self.model.query(self.query)
            # Store decoding in accumulators
            self._out_state = self.model.decode()
            self._logger.debug(f"Decoded state: {self._out_state}")
            self._out_burst = self.burst(self._out_state)
            self._logger.debug(f"Burst: {self._out_burst}")
