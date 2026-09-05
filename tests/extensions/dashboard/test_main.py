"""Tests for the dashboard command-line entry point."""

from unittest.mock import Mock

from pytest import MonkeyPatch

from qrobot_dashboard import __main__


def test_parse_args_uses_local_defaults() -> None:
    """The command starts locally on the conventional Dash port by default."""
    args = __main__.parse_args([])
    assert (args.host, args.port) == ("127.0.0.1", 8050)


def test_parse_args_accepts_host_and_port() -> None:
    """Both bind settings can be overridden from the command line."""
    args = __main__.parse_args(["--host", "0.0.0.0", "--port", "9000"])
    assert (args.host, args.port) == ("0.0.0.0", 9000)


def test_main_runs_app_without_debug_or_reloader(monkeypatch: MonkeyPatch) -> None:
    """The command starts exactly one production-like development process."""
    server = Mock()
    monkeypatch.setattr(__main__, "create_app", Mock(return_value=server))
    __main__.main(["--host", "localhost", "--port", "9000"])
    server.run.assert_called_once_with(host="localhost", port=9000, debug=False, use_reloader=False)
