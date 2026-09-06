from unittest.mock import Mock

from qrobot_qunits.redis import RedisConfig, flush_redis, get_redis, read_outputs, redis_status
from qrobot_qunits.redis import utils


def test_read_outputs_batches_keys_and_preserves_order() -> None:
    # Preparing three Redis results in the same order as their input IDs.
    client = Mock()
    client.mget.return_value = ["0.25", None, 1.0]

    # Reading the outputs and checking both their values and requested keys.
    assert read_outputs(client, ["left", "missing", "right"]) == ["0.25", None, "1.0"]
    client.mget.assert_called_once_with(["left output", "missing output", "right output"])


def test_read_outputs_avoids_empty_redis_request() -> None:
    # Preparing a Redis client, then reading an empty list of input IDs.
    client = Mock()

    # Checking that no Redis request is made when there are no inputs.
    assert read_outputs(client, []) == []
    client.mget.assert_not_called()


def test_redis_status_omits_key_deleted_between_scan_and_read(monkeypatch) -> None:
    # Preparing one existing output and one output deleted before it is read.
    client = Mock()
    client.scan_iter.return_value = iter(("still-there output", "deleted output"))
    client.mget.return_value = ["0.5", None]
    monkeypatch.setattr(utils, "get_redis", Mock(return_value=client))

    # Reading the database and checking that only the existing output is returned.
    assert redis_status() == {"still-there output": "0.5"}
    client.mget.assert_called_once_with(["still-there output", "deleted output"])


def test_redis_status_avoids_read_for_empty_database(monkeypatch) -> None:
    # Preparing a scan that finds no keys in the database.
    client = Mock()
    client.scan_iter.return_value = iter(())
    monkeypatch.setattr(utils, "get_redis", Mock(return_value=client))

    # Checking that the result is empty without asking Redis for values.
    assert redis_status() == {}
    client.mget.assert_not_called()


def test_get_redis_applies_config_and_decodes_responses(monkeypatch) -> None:
    # Replacing the Redis constructor so its connection settings can be checked.
    client = Mock()
    client_factory = Mock(return_value=client)
    monkeypatch.setattr("qrobot_qunits.redis.utils.redis.Redis", client_factory)

    # Creating the client and checking the host, port, database and text decoding.
    assert get_redis(RedisConfig("host", 6380, 4)) is client
    client_factory.assert_called_once_with(host="host", port=6380, db=4, decode_responses=True)


def test_flush_redis_flushes_selected_database(monkeypatch) -> None:
    # Preparing a Redis mock for database 9.
    client = Mock()
    monkeypatch.setattr(utils, "get_redis", Mock(return_value=client))

    # Clearing that database and checking that flushdb is called once.
    flush_redis(RedisConfig(database=9))

    client.flushdb.assert_called_once_with()
