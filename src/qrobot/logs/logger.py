"""
Module containing logging utilities
"""

# import inspect
import logging
import os
import sys

# from datetime import datetime
from logging.handlers import TimedRotatingFileHandler

LOGS_DIR = os.path.join(os.getcwd(), ".qrobot_logs")
LOG_FILE = os.path.join(LOGS_DIR, "qrobot.log")

FORMATTER = logging.Formatter(
    "%(asctime)s — %(name)s — %(levelname)s — "
    + "%(funcName)s:%(lineno)d — %(message)s"
)


def get_console_handler():
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(FORMATTER)
    console_handler.setLevel(logging.INFO)
    return console_handler


def get_file_handler():
    if not os.path.exists(LOGS_DIR):
        os.makedirs(LOGS_DIR)
    file_handler = TimedRotatingFileHandler(LOG_FILE, when="midnight")
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
