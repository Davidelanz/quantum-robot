# Dashboard

The dashboard reads qUnit state from Redis on `localhost:6379`.
If Redis is not already running, start it in Docker:

```sh
docker run --rm --name qrobot-redis -p 6379:6379 -d redis:7-alpine
```

To then start the dashboard:

```sh
poetry run python -m qrobot_dashboard
```

The dashboard will be exposed at <http://127.0.0.1:8050>.
It discovers qUnits from Redis automatically and refreshes every second.
Stop the dashboard with Ctrl+C.
To change the dashboard port to `NEW_PORT`, pass `--port NEW_PORT` at startup.

The dashboard displays qUnits in the shared Redis database and refreshes automatically every second. With an empty database, the graph starts empty; qUnits appear as your application registers them.
Use the refresh slider to select an interval from 0.5 to 10 seconds.
Longer intervals reduce the dashboard's CPU and Redis activity while running compute-intensive simulations.

```{eval-rst}
.. automodule:: qrobot_dashboard.app
   :members:
```
