from unittest.mock import Mock

from qrobot_qunits.redis import RedisConfig, flush_redis, get_redis, redis_status
from qrobot_qunits.redis import utils


def test_redis_status_omits_key_deleted_between_scan_and_get(monkeypatch) -> None:
    client = Mock()
    client.scan_iter.return_value = iter(("still-there output", "deleted output"))
    client.get.side_effect = ("0.5", None)
    monkeypatch.setattr(utils, "get_redis", Mock(return_value=client))

    assert redis_status() == {"still-there output": "0.5"}


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
