"""Real sensor-to-qUnit processing with shared runtime configuration."""

import json
import pytest
from qrobot.bursts import ZeroBurst
from qrobot.models import AngularModel
from qrobot_qunits import QUnit, SensorialUnit

pytestmark = pytest.mark.redis


def test_qunit_lifecycle(redis_runtime):
    """Workers process full windows and publish query and input connections changes."""
    config, client, units, wait_for = redis_runtime

    # Preparing the units and their input connections.
    sensor = SensorialUnit("source", 0.02, redis_config=config)
    other = SensorialUnit("other", 0.02, default_input=1.0, redis_config=config)
    unit = QUnit(
        "processor",
        AngularModel(n=1, tau=2),
        ZeroBurst(),
        0.02,
        in_qunits={0: sensor.id},
        redis_config=config,
    )
    # Registering every unit so the fixture cleans up even if a check fails.
    units.extend([sensor, other, unit])
    # Starting the sensors and the qUnit as separate processes.
    for worker in units:
        worker.start()
    # Waiting until the qUnit has read enough input samples to produce an output.
    wait_for(lambda: unit.get_burst_output() is not None)
    # Checking that the running unit has produced an output between zero and one.
    output = unit.get_burst_output()
    assert output is not None
    assert 0 <= output <= 1
    # Changing the query and selected input while the qUnit is running.
    unit.query = [0.75]
    unit.set_input(0, other.id)
    wait_for(
        lambda: (
            client.get(f"{unit.id} query") == "[0.75]"
            and json.loads(client.get(f"{unit.id} in_qunits")) == {"0": other.id}
        )
    )
    assert client.get(f"{unit.id} state") is not None
    # Checking that the workers are still running before shutting them down.
    processes = []
    for worker in units:
        process = worker._loop_thread
        assert process is not None
        processes.append(process)
    assert all(process.is_alive() for process in processes)
    # Stopping all workers and checking that their Redis keys are gone.
    for worker in reversed(units):
        worker.stop()
        assert list(client.scan_iter(match=f"{worker.id} *")) == []
    assert all(not process.is_alive() for process in processes)
