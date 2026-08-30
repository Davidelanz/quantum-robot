"""Redis configuration and operations used by the qUnits extension."""

from dataclasses import dataclass

import redis

from qrobot.logger import get_logger


@dataclass(frozen=True)
class RedisConfig:
    """Connection settings for a Redis database used by qUnits.

    Parameters
    ----------
    host : str
        Redis server hostname. Defaults to ``"localhost"``.
    port : int
        Redis server port. Defaults to ``6379``.
    database : int
        Redis logical database number. Defaults to ``0``.
    """

    host: str = "localhost"
    port: int = 6379
    database: int = 0


class RedisWriteError(RuntimeError):
    """Raised when a qUnit cannot persist its state to Redis."""


def get_redis(config: RedisConfig | None = None) -> redis.Redis:
    """Return a Redis client with decoded string responses.

    Parameters
    ----------
    config : RedisConfig | None
        Connection settings. When omitted, use the local default Redis server.

    Returns
    -------
    redis.Redis
        A lazily connected ``redis-py`` client configured with
        ``decode_responses=True``.
    """
    settings = config or RedisConfig()
    return redis.Redis(
        host=settings.host,
        port=settings.port,
        db=settings.database,
        decode_responses=True,
    )


def redis_status(config: RedisConfig | None = None) -> dict[str, str]:
    """Return the current key/value status of a Redis database.

    Parameters
    ----------
    config : RedisConfig | None
        Connection settings for the database to inspect.

    Returns
    -------
    dict[str, str]
        Mapping of every existing key to its decoded string value. Keys deleted
        while scanning are omitted.
    """
    client = get_redis(config)
    status: dict[str, str] = {}
    for key in client.scan_iter():
        value = client.get(key)
        if value is not None:
            status[str(key)] = str(value)
    return status


def flush_redis(config: RedisConfig | None = None) -> None:
    """Remove every key from the configured Redis logical database.

    Parameters
    ----------
    config : RedisConfig | None
        Connection settings for the database to clear. The default is database
        ``0`` on the local Redis server.

    Warning
    -------
    This operation is destructive for the selected Redis logical database.
    """
    logger = get_logger("redis")
    logger.info("Flushing Redis database")
    client = get_redis(config)
    client.flushdb()
