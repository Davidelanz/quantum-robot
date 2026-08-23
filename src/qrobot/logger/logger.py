"""Logging helpers for the quantum-robot library.

Applications configure handlers, destinations, and verbosity. quantum-robot only
returns named loggers and installs a ``NullHandler`` on its package logger so
library use never changes the caller's global logging configuration.
"""

import logging
import sys
from dataclasses import dataclass
from pathlib import Path

_PACKAGE_LOGGER_NAME = "qrobot"
logging.getLogger(_PACKAGE_LOGGER_NAME).addHandler(logging.NullHandler())


@dataclass(frozen=True)
class LoggingConfig:
    """Optional application-owned logging configuration for quantum-robot.

    Parameters
    ----------
    level : int
        Standard-library logging level. Defaults to ``logging.INFO``.
    file_path : Path | None
        Optional destination for a rotating debug log. No file is created when
        omitted.
    console : bool
        Whether to emit records to standard output. Defaults to ``True``.
    """

    level: int = logging.INFO
    file_path: Path | None = None
    console: bool = True


def get_logger(logger_name: str) -> logging.Logger:
    """Return a qrobot-namespaced logger without configuring any handlers."""
    return logging.getLogger(f"{_PACKAGE_LOGGER_NAME}.{logger_name}")


def configure_logging(config: LoggingConfig) -> logging.Logger:
    """Configure quantum-robot logging explicitly for an application.

    Only handlers previously installed by this function are replaced. This
    keeps repeated setup calls idempotent without changing unrelated logging
    configuration owned by the application.
    """
    logger = logging.getLogger(_PACKAGE_LOGGER_NAME)
    logger.setLevel(config.level)
    logger.propagate = False

    for handler in logger.handlers[:]:
        if getattr(handler, "_qrobot_managed", False):
            logger.removeHandler(handler)
            handler.close()

    formatter = logging.Formatter("%(asctime)s — %(name)s — %(levelname)s — %(message)s")
    if config.console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        console_handler.setLevel(config.level)
        console_handler._qrobot_managed = True  # type: ignore[attr-defined]
        logger.addHandler(console_handler)
    if config.file_path is not None:
        config.file_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(config.file_path)
        file_handler.setFormatter(formatter)
        file_handler.setLevel(config.level)
        file_handler._qrobot_managed = True  # type: ignore[attr-defined]
        logger.addHandler(file_handler)
    return logger
