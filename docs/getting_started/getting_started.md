# Getting Started

## Install quantum-robot

`quantum-robot` supports Python 3.11 through 3.14. Creating a virtual environment keeps its
dependencies separate from system Python:

```console
python3.14 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install --upgrade quantum-robot
```

On Windows PowerShell, activate the environment with
`.venv\Scripts\Activate.ps1` instead.

Optional functionality is provided by extras in the same distribution:

```console
python -m pip install --upgrade "quantum-robot[model-visualization]"
python -m pip install --upgrade "quantum-robot[qunits]"
python -m pip install --upgrade "quantum-robot[visualization]"
python -m pip install --upgrade "quantum-robot[simulator]"
python -m pip install --upgrade "quantum-robot[dashboard]"
```

The extension imports are `qrobot_qunits`, `qrobot_visualization`,
`qrobot_simulator`, and `qrobot_dashboard`. The `model-visualization` extra
adds the plotting dependencies used by model methods. Extras install only the
dependencies for that capability; all import packages ship in the same
distribution. Multiple extras can be installed together, for example:

```console
python -m pip install --upgrade "quantum-robot[qunits,simulator]"
```

Check the core installation before continuing:

```console
python -c "import qrobot; from qrobot.backends import QiskitBackend; print('quantum-robot is ready')"
```

For development from a checkout, Poetry creates and manages the environment:

```console
git clone https://github.com/Davidelanz/quantum-robot.git
cd quantum-robot
poetry env use 3.14
poetry install --all-extras
```

This installs every application and development extra declared in
`pyproject.toml`, including test, documentation, and lint tooling. Verify the
checkout with:

```console
poetry check
poetry run pytest -m "not redis"
```

## Redis database

The optional `qunits` extra, which exposes `qrobot_qunits`, requires
[Redis](https://redis.io), an in-memory data store used for communication
between independently timed units.

<figure class="align-center">
<img
src="https://github.com/dspezia/redis-doc/raw/client_command/topics/Data_size.png"
width="400"
alt="Check the How fast is Redis? benchmark page for further information" />
<figcaption aria-hidden="true">Check the <a
href="https://redis.io/topics/benchmarks">How fast is Redis?</a>
benchmark page for further information</figcaption>
</figure>

- To install Redis, check
  [redis.io/docs/getting-started/installation/](https://redis.io/docs/getting-started/installation/)
- The [redis-py](https://github.com/redis/redis-py) Python package is installed
  by the `qunits`, `simulator`, and `dashboard` extras.

```{note}
On Linux, start a locally installed Redis server with
`service redis-server start`.
```

It is also possible to use Docker to start Redis without installing it on the
local machine:

```console
docker run --rm --name qrobot-redis -p 6379:6379 -d redis:7-alpine
```

Stop it with:

```console
docker stop qrobot-redis
docker rm qrobot-redis
```

To check whether Redis is reachable, run:

```console
python -c "from qrobot_qunits.redis.utils import redis_status; print(redis_status())"
```

With Redis running, try one of the packaged simulations from a repository
checkout:

```console
poetry run python examples/grasping_robot.py
poetry run python examples/bug_world.py
```
