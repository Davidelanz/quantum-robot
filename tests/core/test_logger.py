"""Tests for quantum-robot's library logging contract."""

import logging

from qrobot.logger import LoggingConfig, configure_logging, get_logger


def test_logger_is_namespaced_and_leaves_caller_configuration_untouched(
    caplog, tmp_path, monkeypatch
) -> None:
    """Library logging is observable but never creates handlers or files."""
    monkeypatch.chdir(tmp_path)
    logger = get_logger("test")
    caplog.set_level(logging.INFO, logger=logger.name)

    logger.info("hello from qrobot")

    assert logger.name == "qrobot.test"
    assert "hello from qrobot" in caplog.text
    assert logger.handlers == []
    assert not (tmp_path / ".qrobot_logs").exists()


def test_explicit_logging_configuration_writes_only_the_requested_file(
    tmp_path,
) -> None:
    """Applications can opt into an idempotent file-based debug setup."""
    log_path = tmp_path / "debug.log"
    package_logger = configure_logging(
        LoggingConfig(level=logging.DEBUG, file_path=log_path, console=False)
    )

    try:
        get_logger("test").debug("configured debug message")
        for handler in package_logger.handlers:
            handler.flush()

        assert "configured debug message" in log_path.read_text()
        assert (
            sum(
                getattr(handler, "_qrobot_managed", False)
                for handler in package_logger.handlers
            )
            == 1
        )
    finally:
        configure_logging(LoggingConfig(console=False))
