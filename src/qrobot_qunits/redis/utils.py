"""Redis configuration and operations used by the qUnits extension."""

from dataclasses import dataclass
from collections.abc import Iterable

import redis

from qrobot.logger import get_logger
from .protocol import RedisAttribute, build_redis_key


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
    keys = list(client.scan_iter())
    if not keys:
        return {}
    values = client.mget(keys)
    return {str(key): str(value) for key, value in zip(keys, values) if value is not None}


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


def read_outputs(client: redis.Redis, unit_ids: Iterable[str]) -> list[str | None]:
    """Read several unit outputs in one Redis request.

    Parameters
    ----------
    client : redis.Redis
        Connected Redis client configured to decode responses.
    unit_ids : collections.abc.Iterable[str]
        Unit identifiers in the order their outputs should be returned.

    Returns
    -------
    list of str or None
        Output values aligned with ``unit_ids``. Missing keys produce ``None``.
    """
    keys = [build_redis_key(unit_id, RedisAttribute.OUTPUT) for unit_id in unit_ids]
    if not keys:
        return []
    return [None if value is None else str(value) for value in client.mget(keys)]
