"""Classical gripper that decides from averages of recent sensor readings."""

from .base_gripper import BaseGripper, BaseGripperBrain, Diagnostics, Readings
from .config import CLASSICAL_GRIPPER_CONFIG, ClassicalGripperConfig


class FixedWindowIntegrator:
    """Collect a fixed number of sensor readings and return their average.

    Readings are collected once per ``sampling_period``. After ``window_size``
    readings, their average becomes the new output and collection starts again.
    While a group is still incomplete, the previous average remains available.
    """

    def __init__(self, sampling_period: float, window_size: int, initial_value: float) -> None:
        """Validate timing and initialize the completed-window output."""
        if sampling_period <= 0:
            raise ValueError("sampling_period must be positive")
        if window_size <= 0:
            raise ValueError("window_size must be positive")
        self.sampling_period = sampling_period
        self.window_size = window_size
        self._output = initial_value
        self._samples: list[float] = []
        self._elapsed = 0.0

    @property
    def output(self) -> float:
        """Return the average of the last complete group of readings."""
        return self._output

    def reset(self, initial_value: float) -> None:
        """Discard an incomplete group and restore the initial output."""
        self._output = initial_value
        self._samples.clear()
        self._elapsed = 0.0

    def update(self, value: float, dt: float) -> float:
        """Collect readings due during ``dt`` and return the available average."""
        if dt <= 0:
            raise ValueError("dt must be positive")
        self._elapsed += dt

        # A physics update may span several sampling instants. Treat the latest
        # reading as held throughout that interval, as the sensorial units do
        # between publications.
        while self._elapsed + 1e-12 >= self.sampling_period:
            self._elapsed -= self.sampling_period
            self._samples.append(value)
            if len(self._samples) == self.window_size:
                self._output = sum(self._samples) / self.window_size
                self._samples.clear()
        return self._output


class ClassicalGripperBrain(BaseGripperBrain):
    """Close and open the jaws from recent proximity and touch readings.

    The brain averages proximity over a short period, so one isolated near
    reading is insufficient to close the jaws. It averages touch over a longer
    period. An empty gripper produces a high touch value and contact produces a
    low one. The averages are combined into one command: strong recent proximity
    while the gripper is available favors closing; losing proximity or accumulating
    contact evidence favors opening.

    The two averaging periods equal the periods observed by the quantum brain.
    This makes it possible to compare ordinary averaging with the AngularModel
    without giving either robot a longer sensor history.
    """

    def __init__(self, config: ClassicalGripperConfig) -> None:
        """Create separate averages for ball proximity and jaw contact."""
        self.config = config
        self.proximity = FixedWindowIntegrator(
            config.sampling_period,
            config.proximity_tau,
            initial_value=0.0,
        )
        self.empty_gripper = FixedWindowIntegrator(
            config.sampling_period,
            config.empty_gripper_tau,
            initial_value=1.0,
        )
        self._activation = 0.0

    def start(self, readings: Readings) -> None:
        """Initialize both outputs from the sensor state before simulated time."""
        self.proximity.reset(readings["proximity"])
        self.empty_gripper.reset(readings["touch"])
        self._activation = self._actuator_output()

    @property
    def ready(self) -> bool:
        """Return true because both initial outputs are immediately available."""
        return True

    def command(self, readings: Readings, dt: float) -> float:
        """Update both sensor averages and return an open or closed command."""
        self.proximity.update(readings["proximity"], dt)
        self.empty_gripper.update(readings["touch"], dt)
        self._activation = self._actuator_output()
        return self._activation

    def stop(self) -> None:
        """Accept the common lifecycle call; no resources require cleanup."""

    def diagnostics(self) -> Diagnostics:
        """Return the sensor averages and current jaw command for display."""
        return {
            "proximity_mean": self.proximity.output,
            "empty_gripper_mean": self.empty_gripper.output,
            "gripper_activation": self._activation,
        }

    def _actuator_output(self) -> float:
        """Use the same strict normalized-mean threshold as ActuatorUnit."""
        normalized_sum = (self.proximity.output + self.empty_gripper.output) / 2
        return float(normalized_sum > self.config.gripper_threshold)


class ClassicalGripper(BaseGripper):
    """Gripper that filters recent readings with ordinary arithmetic averages."""

    def __init__(
        self,
        config: ClassicalGripperConfig = CLASSICAL_GRIPPER_CONFIG,
        brain: BaseGripperBrain | None = None,
    ) -> None:
        """Use the configured classical brain unless another brain is supplied."""
        selected_brain = brain if brain is not None else ClassicalGripperBrain(config)
        super().__init__(config, selected_brain)
