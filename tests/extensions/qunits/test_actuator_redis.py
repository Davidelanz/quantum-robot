"""Real input workers drive actuator activation and inhibition."""

import pytest
from qrobot_qunits import ActuatorUnit, SensorialUnit

pytestmark = pytest.mark.redis


def test_actuator_lifecycle(redis_runtime):
    """Changing live input outputs crosses the actuator's strict threshold."""
    config, client, units, wait_for = redis_runtime

    # Preparing the units and their input connections.
    sources = [SensorialUnit(name, 0.02, redis_config=config) for name in ("left", "right")]
    actuator = ActuatorUnit("gripper", [source.id for source in sources], 0.02, redis_config=config)
    # Registering every unit so the fixture cleans up even if a check fails.
    units.extend([*sources, actuator])
    # Starting the real worker processes.
    for unit in units:
        unit.start()
    # Reading the first actuator output and checking that zero inputs keep it off.
    wait_for(lambda: actuator.get_activation() == 0.0)
    # Setting both sensor outputs to one and waiting for activation.
    for source in sources:
        source.scalar_reading = 1.0
    # Reading the new output and checking that two high inputs turn it on.
    wait_for(lambda: actuator.get_activation() == 1.0)
    # Checking that the input average written to Redis is one.
    assert float(client.get(f"{actuator.id} input")) == 1.0
    # Lowering one input: an average equal to the threshold must turn the output off.
    sources[0].scalar_reading = 0.0
    wait_for(lambda: actuator.get_activation() == 0.0)
    assert float(client.get(f"{actuator.id} input")) == 0.5
    # Checking that the workers are still running before shutting them down.
    processes = []
    for unit in units:
        process = unit._loop_thread
        assert process is not None
        processes.append(process)
    assert all(process.is_alive() for process in processes)
    # Stopping all workers and checking that their Redis keys are gone.
    for unit in reversed(units):
        unit.stop()
        assert list(client.scan_iter(match=f"{unit.id} *")) == []
    assert all(not process.is_alive() for process in processes)
