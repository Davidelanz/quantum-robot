"""Real sensor startup, shared reading updates, restart and shutdown."""

import pytest
from qrobot_qunits import SensorialUnit

pytestmark = pytest.mark.redis


def test_sensor_lifecycle(redis_runtime):
    """A child publishes parent-side updates and can restart after cleanup."""
    config, client, units, wait_for = redis_runtime

    # Preparing the units and their input connections.
    sensor = SensorialUnit("distance", 0.02, default_input=0.25, redis_config=config)
    # Registering the sensor for cleanup even if a check fails.
    units.append(sensor)
    # Repeating startup and shutdown to check that the same sensor can restart.
    for reading in (0.75, 0.5):
        sensor.start()
        process = sensor._loop_thread
        # start() must create the process before the test can inspect it.
        assert process is not None
        assert process.is_alive()
        assert client.get(f"{sensor.id} class") == "SensorialUnit"
        # Updating the reading here and checking the output written by the child process.
        sensor.scalar_reading = reading
        wait_for(lambda: client.get(f"{sensor.id} output") == str(reading))
        # Stopping the child process and checking that its keys were removed.
        sensor.stop()
        assert not process.is_alive()
        assert list(client.scan_iter(match=f"{sensor.id} *")) == []
