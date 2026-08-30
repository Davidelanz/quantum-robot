import pytest

from qrobot_qunits.redis import (
    RedisAttribute,
    RedisKey,
    build_redis_key,
    parse_redis_key,
)


def test_redis_key_round_trip_preserves_spaces_in_unit_id() -> None:
    key = build_redis_key("sensor output monitor", RedisAttribute.OUTPUT)

    assert key == "sensor output monitor output"
    assert parse_redis_key(key) == RedisKey("sensor output monitor", RedisAttribute.OUTPUT)


@pytest.mark.parametrize(
    "key",
    ["", "sensor", "sensor unknown", " output", " sensor output", "sensor output "],
)
def test_parse_redis_key_rejects_malformed_keys(key: str) -> None:
    assert parse_redis_key(key) is None


def test_build_redis_key_rejects_unknown_attributes() -> None:
    with pytest.raises(ValueError, match="unknown Redis attribute"):
        build_redis_key("sensor", "unknown")
