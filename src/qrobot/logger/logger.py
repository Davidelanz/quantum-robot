"""Module containing logging utilities."""

import logging
import sys
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

FORMATTER = logging.Formatter(
    "%(asctime)s — %(name)s — %(levelname)s — "
    + "%(funcName)s:%(lineno)d — %(message)s"
)


def log_dir() -> Path:
    """Return the path to the directory storing logs."""
    return Path.cwd().joinpath(".qrobot_logs")


def log_file() -> Path:
    """Return the path to the current log file."""
    return log_dir().joinpath("qrobot.log")


def get_console_handler():
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(FORMATTER)
    console_handler.setLevel(logging.INFO)
    return console_handler


def get_file_handler():
    log_dir().mkdir(parents=True, exist_ok=True)
    file_handler = TimedRotatingFileHandler(log_file(), when="midnight")
    file_handler.setFormatter(FORMATTER)
    file_handler.setLevel(logging.DEBUG)
    return file_handler


def get_logger(logger_name):
    logger = logging.getLogger(logger_name)
    # better to have too much log than not enough
    logger.setLevel(logging.DEBUG)
    logger.addHandler(get_console_handler())
    logger.addHandler(get_file_handler())
    # with this pattern, it's rarely necessary to propagate the error up to parent
    logger.propagate = False
    return logger
