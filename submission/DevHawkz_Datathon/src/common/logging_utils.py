"""Safe local console logging for WayLoom pipelines."""

from __future__ import annotations

import logging
import sys


_HANDLER_MARKER = "_wayloom_console_handler"


def get_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """Return a local console logger without duplicate handlers.

    Callers should log stage names, counts, durations, and validation summaries.
    They must not pass private rows, full DataFrames, secrets, or credentials.
    """

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.propagate = False

    handler = next(
        (
            existing
            for existing in logger.handlers
            if getattr(existing, _HANDLER_MARKER, False)
        ),
        None,
    )
    if handler is None:
        handler = logging.StreamHandler(sys.stdout)
        setattr(handler, _HANDLER_MARKER, True)
        handler.setFormatter(
            logging.Formatter(
                "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
            )
        )
        logger.addHandler(handler)

    for existing in logger.handlers:
        existing.setLevel(level)

    return logger
