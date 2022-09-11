import redis

from ..logs import get_logger


def get_redis(
    host: str = "localhost",
    port: int = 6379,
    database: int = 0,
) -> redis.Redis:
    """Returns a redis-py Redis client.

    Parameters
    ------------
    host : str
        Redis server hostname. Defaults to "localhost".
    port : int
        Redis server port. Defaults to 6379.
    database : int
        Redis database. Defaults to 0.

    Returns
    ------------
    redis.Redis
        redis-py Redis client

    See Also
    --------
    redis.Redis : `redis-py Redis client class <https://redis-py.\
        readthedocs.io/en/stable/connections.html#redis.Redis>`_
    """
    return redis.Redis(host, port, database)


def redis_status(
    host: str = "localhost",
    port: int = 6379,
    database: int = 0,
) -> dict:
    """Returns the current redis database status in the for of a dictionary
    with ``{db_key : db_value}`` mapping.

    Parameters
    ------------
    host : str
        Redis server hostname. Defaults to "localhost".
    port : int
        Redis server port. Defaults to 6379.
    database : int
        Redis database. Defaults to 0.

    Returns
    ------------
    dict
        Redis current status
    """
    _r = get_redis(host, port, database)
    status = {}
    for key in _r.scan_iter():
        status[key.decode("ascii")] = _r.get(key).decode("ascii")
    return status


def flush_redis(
    host: str = "localhost",
    port: int = 6379,
    database: int = 0,
) -> None:
    """Flush the redis database.

    Parameters
    ------------
    host : str
        Redis server hostname. Defaults to "localhost".
    port : int
        Redis server port. Defaults to 6379.
    database : int
        Redis database. Defaults to 0.
    """
    logger = get_logger("redis")
    logger.info("Flushing redis database")
    logger.debug(f"Previous redis state: {redis_status()}")
    _r = get_redis(host, port, database)
    _r.flushdb()
    logger.debug(f"Current redis state: {redis_status()}")
