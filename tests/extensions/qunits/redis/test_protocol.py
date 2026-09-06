import pytest

from qrobot_qunits.redis import (
    RedisAttribute,
    RedisKey,
    build_redis_key,
    parse_redis_key,
)


def test_redis_key_round_trip_preserves_spaces_in_unit_id() -> None:
    # Preparing a unit ID containing spaces and building its output key.
    key = build_redis_key("sensor output monitor", RedisAttribute.OUTPUT)

    # Checking the key text and reading it back into its two parts.
    assert key == "sensor output monitor output"
    assert parse_redis_key(key) == RedisKey("sensor output monitor", RedisAttribute.OUTPUT)


def test_build_redis_key_rejects_unknown_attributes() -> None:
    # Trying to build a key with an output name outside the supported list.
    with pytest.raises(ValueError, match="unknown Redis attribute"):
        build_redis_key("sensor", "unknown")


@pytest.mark.parametrize(
    "unit_id, error",
    [(None, TypeError), ("", ValueError), (" sensor", ValueError), ("sensor ", ValueError)],
)
def test_build_redis_key_rejects_invalid_unit_ids(unit_id, error):
    """Identifiers must be non-empty strings without surrounding whitespace."""
    # Trying each invalid ID and checking the expected validation error.
    with pytest.raises(error):
        build_redis_key(unit_id, RedisAttribute.OUTPUT)


@pytest.mark.parametrize(
    "key",
    [None, "", "sensor", "sensor unknown", " output", " sensor output", "sensor output "],
)
def test_parse_redis_key_rejects_malformed_keys(key: str) -> None:
    # Reading malformed keys and checking that none is accepted.
    assert parse_redis_key(key) is None
