"""
Python script for running a single monodimensional qUnit
"""

import json
import time

import qrobot
from qrobot.bursts import ZeroBurst
from qrobot.models import AngularModel


def heading_ui(string: str):
    print(
        "\n========================================\n"
        + string
        + "\n========================================\n"
    )


def redis_status_ui():
    status = qrobot.qunits.qunit.redis_status()
    print("Redis status:")
    print(json.dumps(status, indent=1))


heading_ui(f"Script {__file__} started")


heading_ui("Initializing qUnit")
l0_unit0 = qrobot.qunits.QUnit(
    name="lo_unit0",
    model=AngularModel(n=1, tau=10),
    burst=ZeroBurst(),
    Ts=0.05,
    query=[0.5],  # Query target initialized
    # No input
)
print(l0_unit0)

heading_ui("Starting qUnit")
l0_unit0.start()

heading_ui("Check redis status for 10 seconds")
for _ in range(20):
    redis_status_ui()
    time.sleep(1)

heading_ui("Stopping")

redis_status_ui()
l0_unit0.stop()
redis_status_ui()

heading_ui("Script ended")
