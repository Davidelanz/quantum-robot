import multiprocessing
from uuid import uuid4  # unique identifier generator

import rospy
from std_msgs.msg import Float32, String

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

    def __repr__(self) -> str:
        return f"QUnit \"{self.name}\" | name={self.name} | n={self.n} | " +\
            "tau={self.tau} | Ts={self.Ts} | query={self.query}"

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
        self._logger.debug(str(self))

        # Initialize input data accumulator
        self._in_data = [.0]*self.n

        # Initialize background thread
        self.process = None

    def _input_callback(self, msg, i: int) -> None:
        """ROS callback for input data. The parameter ``i`` refers to the
        ``i``-th topic subscribed (same callback for all the subscribers)
        """
        self._in_data[i] = msg.data

    def start(self) -> None:
        """Runs the qUnit in a background thread"""
        self._logger.debug(f"Starting qUnit {self.id}")
        # New instance of a process
        self._process = multiprocessing.Process(target=self._loop)
        # Start looping
        self._process.start()

    def stop(self) -> None:
        """Stops the qUnit background thread"""
        if self._process is None:
            self._logger.warning(
                "Trying to stop qUnit, but it is not running")
        else:
            self._logger.info("Stopping qUnit process")
            self._process.terminate()

    def _loop(self) -> None:
        """The main loop of the qUnit"""
        # Initialize the ROS node
        rospy.init_node(self.id, anonymous=False)
        self._logger.debug(f"Rospy node started")

        # Define iteratively n subscribers
        for i in range(self.model.n):
            s = rospy.Subscriber(
                name=f'/{self.id}/input_{i}', data_class=Float32,
                callback=self._input_callback, callback_args=i)
            self._logger.debug(f"subscribed to {s.name}")

        # Define the publishers
        self._state_pub = rospy.Publisher(
            f"/{self.id}/state", String, queue_size=2)
        self._logger.debug(f"publishing on {self._state_pub.name}")
        self._burst_pub = rospy.Publisher(
            f"/{self.id}/burst", Float32, queue_size=2)
        self._logger.debug(f"publishing on {self._burst_pub.name}")

        # Main loop of the ROS node:
        rate = rospy.Rate(1/self.Ts)
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
                rate.sleep()
            # After the time window, apply the query
            if self.query is not None:
                self._logger.debug(f"Querying for state {self.query}")
                self.model.query(self.query)
            # Prepare the messages to be published
            msg_state = String
            msg_burst = Float32
            # Then, decode the state anf get the burst
            msg_state.data = self.model.decode()
            self._logger.debug(f"Decoded state: {msg_state.data}")
            msg_burst.data = self.burst(msg_state.data)
            self._logger.debug(f"Burst: {msg_state.data}")
            # Publish the results
            self._state_pub.publish(msg_state)
            self._burst_pub.publish(msg_burst)
            self._logger.debug("State and burst messages published")
