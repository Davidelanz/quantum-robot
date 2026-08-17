# Redis database

The optional `qunits` extra, which exposes `qrobot_qunits`, requires
[Redis](https://redis.io), a high performance, super fast and easy to
use in-memory database.

<figure class="align-center">
<img
src="https://github.com/dspezia/redis-doc/raw/client_command/topics/Data_size.png"
width="400"
alt="Check the How fast is Redis? benchmark page for further information" />
<figcaption aria-hidden="true">Check the <a
href="https://redis.io/topics/benchmarks">How fast is Redis?</a>
benchmark page for further information</figcaption>
</figure>

- To install redis, check
  [redis.io/docs/getting-started/installation/](https://redis.io/docs/getting-started/installation/)
- The [redis-py](https://github.com/andymccurdy/redis-py) pyhon package
  is what is used by quantum-robot to connect to the redis database
  ([redis.io/clients#python](https://redis.io/clients#python)).

```{note}
On Linux, start a locally installed Redis server with
`service redis-server start`.
```

It is also possible to use Docker to spin a redis server without
installing redis on your local machine:

``` shell
docker run --name redis_container -p 6379:6379 -d redis
```

The to stop it:

``` shell
docker stop redis_container
docker rm redis_container
```

To check wether the redis database is reachable, open a python shell
(for example, `python` in the installed environment) and run:

``` python
>>> from qrobot_qunits.redis_utils import redis_status
>>> redis_status()
```
