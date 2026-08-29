"""Tests for normalized sensorial-unit readings."""

from qrobot_qunits import SensorialUnit


def test_invalid_reading_uses_default_input() -> None:
    sensor = SensorialUnit("distance", 0.1, default_input=0.25)
    try:
        # An out-of-range sensor assignment falls back to the configured input.
        sensor.scalar_reading = -0.01
        assert sensor.scalar_reading == 0.25
    finally:
        sensor._multiproc_manager.shutdown()
