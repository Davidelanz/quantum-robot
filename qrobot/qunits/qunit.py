import multiprocessing
from time import sleep
from uuid import uuid4
import ctypes
import json

from pynng import Pub0, Sub0

from ..bursts import Burst
from ..core import Core
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
            query (list): The target state for the model queries.
                Defaults to None

        """
        # Create a instance unique identifier
        self.id = name + "-" + str(uuid4())[:6]
        # use it for log
        self._logger = get_logger(self.id)
        self._logger.debug(f"Initializing qUnit {self.id}")

        # Store the qUnits name and properties
        self.name = name
        self.model = model
        self._burst = burst
        self.Ts = self.period_check(Ts)

        if query is None:
            query = [.0]*(self.model.n)

        # Initialize multiprocessing variables
        # (common to all threads while # being modified)
        manager = multiprocessing.Manager()
        self._query = manager.Array('d', query)
        # Initialize input data accumulator
        self._in_data = manager.Array('d', [.0]*(self.model.n))
        # Initialize output accumulators
        self._out_state = manager.Value(ctypes.c_char_p, "")
        self._out_burst = manager.Value('d', 0)

        # Initialize subscribers dict
        # https://docs.python.org/3/library/multiprocessing.html#proxy-objects
        self._subs = manager.dict({i: None for i in range(model.n)})

        # Initialize publisher
        # (does not need to be managed by multiprocessing, it does not change)
        self._pub = Pub0(listen=Core().address)

        # Initialize threads
        self._loop_thread = None
        self._update_thread = None

        # Log properties
        self._logger.debug(f"Properties: {self}")

    @property
    def subscribers(self) -> dict:
        return {dim: sub for dim, sub in self._subs.items()}

    @property
    def query(self) -> list: return list(self._query)

    def __dict__(self) -> str:
        return {
            "name": self.name,
            "id": self.id,
            "model": str(self.model),
            "subs": self.subscribers,
            "query": self.query,
            "Ts": self.Ts,
        }

    def __repr__(self) -> str:
        out_str = f"QUnit \"{self.id}\""
        for k, v in self.__dict__().items():
            out_str += f"\n     {k}:\t{v}"
        return out_str

    def set_query(self, query) -> str:
        self._logger.debug(f"Changing query from {self._query} to {query}")
        for i, q in enumerate(query):
            self._query[i] = q
        self._logger.debug(f"_query={self._query}")

    def subscribe(self, qunit_id: str, dim: int):
        dim = self.model.dim_index_check(dim)
        self._logger.debug(f"Subscribing to {qunit_id} for dim {dim}")
        self._subs[dim] = qunit_id
        self._logger.debug(f"_subs = {repr(self._subs)}")

    def start(self) -> None:
        """Starts the qUnit background threads"""
        if self._process is not None:
            self._logger.warning("qUnit is already started")
        else:
            self._logger.info("Starting qUnit")
            self._loop_thread = multiprocessing.Process(target=self._loop)
            self._update_thread = multiprocessing.Process(target=self._update)
            self._update_thread.start()
            # Core().add_qunit(self)

    def stop(self) -> None:
        """Stops the qUnit background threads"""
        if self._process is None:
            self._logger.warning("qUnit is already stopped")
        else:
            self._logger.info("Stopping qUnit")
            self._loop_thread.terminate()
            self._update_thread.terminate()
            # Core().remove_qunit(self)

    def period_check(self, Ts) -> float:
        """This method ensures that a `Ts` for the qUnit
        is an integer or a float greater than the global update
        period of the Core.

        Raises
        ---------
        TypeError:
            `Ts` is nor a `int` or a `float`
        ValueError
            `Ts` must not be lower than Core's global update period

        Returns
        --------
        float
            The `Ts`
        """
        if not isinstance(Ts, (float, int)):
            raise TypeError(
                f"Ts must be an scalar number, not a {type(Ts)}!")
        if Ts < Core().T:
            raise ValueError("Ts must not be lower than " +
                             f"Core's period {Core().T}!")
        return float(Ts)

    def _update(self) -> None:
        # Loop through all dimensions
        for dim, qunit_id in self.subscribers.items():
            if qunit_id is None:
                # Store default in vector input
                self._in_data[dim] = 0
            else:
                # Create a subscriber to read what qunit_id is publishing
                sub0 = Sub0(
                    dial=Core().address,
                    recv_timeout=(self.model.tau * self.Ts)
                )
                sub0.subscribe(qunit_id)

                # Read what qunit_id is publishing
                recv_string = sub0.recv()
                recv_dict = json.loads(recv_string.split("#")[-1])
                scalar_input = recv_dict["burst"]
                self._logger.debug(f"Input {scalar_input} on dim={dim}")

                # Store it in the vector input
                self._in_data[dim] = scalar_input

        self._logger.debug(f"_in_data={self._in_data}")

    def _loop(self) -> None:
        while True:

            self._logger.debug("Initializing a new temporal window")
            self.model.clear()
            # "t" is the event index of the temporal window
            for t in range(self.model.tau):

                self._logger.debug("Temporal window event " +
                                   f"{t+1}/{self.model.tau}")

                # Read input
                self.update_in_data()
                self._logger.debug(f"_in_data={self._in_data}")

                # Loop through the dimensions to encode data
                for dim in range(self.model.n):
                    self.model.encode(self._in_data[dim], dim)

                # wait for the next input in the time window
                sleep(self.Ts)

            # After the time window, apply the query
            self._logger.debug(f"Querying for state {self._query}")
            self.model.query(self._query)

            # Publish decoding
            out_state = self.model.decode()
            out_dict = {
                "state": out_state,
                "burst": self._burst(out_state)
            }
            self._logger.debug(f"Output: {out_dict}")
            self._pub.send(f"{self.id}#{out_dict}")
