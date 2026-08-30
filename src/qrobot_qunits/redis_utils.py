"""Compatibility alias for :mod:`qrobot_qunits.redis`.

This module preserves the 1.0.0 import path for external users. Internal code
uses :mod:`qrobot_qunits.redis` directly.
"""

from .redis import (
    RedisAttribute,
    RedisConfig,
    RedisKey,
    RedisWriteError,
    build_redis_key,
    flush_redis,
    get_redis,
    parse_redis_key,
    redis_status,
)

__all__ = [
    "RedisAttribute",
    "RedisConfig",
    "RedisKey",
    "RedisWriteError",
    "build_redis_key",
    "flush_redis",
    "get_redis",
    "parse_redis_key",
    "redis_status",
]
