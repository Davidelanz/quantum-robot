from unittest.mock import Mock

from qrobot_qunits.redis import RedisConfig, flush_redis, get_redis, read_outputs, redis_status
from qrobot_qunits.redis import utils


def test_read_outputs_batches_keys_and_preserves_order() -> None:
    client = Mock()
    client.mget.return_value = ["0.25", None, 1.0]

    assert read_outputs(client, ["left", "missing", "right"]) == ["0.25", None, "1.0"]
    client.mget.assert_called_once_with(["left output", "missing output", "right output"])


def test_read_outputs_avoids_empty_redis_request() -> None:
    client = Mock()

    assert read_outputs(client, []) == []
    client.mget.assert_not_called()


def test_redis_status_omits_key_deleted_between_scan_and_read(monkeypatch) -> None:
    client = Mock()
    client.scan_iter.return_value = iter(("still-there output", "deleted output"))
    client.mget.return_value = ["0.5", None]
    monkeypatch.setattr(utils, "get_redis", Mock(return_value=client))

    assert redis_status() == {"still-there output": "0.5"}
    client.mget.assert_called_once_with(["still-there output", "deleted output"])


def test_redis_status_avoids_read_for_empty_database(monkeypatch) -> None:
    client = Mock()
    client.scan_iter.return_value = iter(())
    monkeypatch.setattr(utils, "get_redis", Mock(return_value=client))

    assert redis_status() == {}
    client.mget.assert_not_called()


def test_get_redis_applies_config_and_decodes_responses(monkeypatch) -> None:
    client_factory = Mock(return_value="client")
    monkeypatch.setattr(utils.redis, "Redis", client_factory)

    assert get_redis(RedisConfig("host", 6380, 4)) == "client"
    client_factory.assert_called_once_with(host="host", port=6380, db=4, decode_responses=True)


def test_flush_redis_flushes_selected_database(monkeypatch) -> None:
    client = Mock()
    monkeypatch.setattr(utils, "get_redis", Mock(return_value=client))

    flush_redis(RedisConfig(database=9))

    client.flushdb.assert_called_once_with()
