"""Behavioural tests for core logging utilities."""

import logging

from qrobot.logger import get_logger, log_dir, log_file


def test_logger_writes_to_project_local_file(tmp_path, monkeypatch) -> None:
    """A logger writes formatted records to the current working directory."""
    monkeypatch.chdir(tmp_path)
    logger = get_logger("qrobot-test-logger")

    try:
        logger.info("core logger contract")
        for handler in logger.handlers:
            handler.flush()

        assert log_dir() == tmp_path / ".qrobot_logs"
        assert log_file() == tmp_path / ".qrobot_logs" / "qrobot.log"
        assert "core logger contract" in log_file().read_text()
        assert any(
            isinstance(handler, logging.StreamHandler) for handler in logger.handlers
        )
    finally:
        for handler in logger.handlers[:]:
            handler.close()
            logger.removeHandler(handler)
