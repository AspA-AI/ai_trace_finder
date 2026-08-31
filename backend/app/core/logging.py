"""Small, dependency-free, colorized logging setup for local operations."""

from __future__ import annotations

import logging
import os
import sys


RESET = "\033[0m"
COLORS = {
    logging.DEBUG: "\033[36m",    # cyan
    logging.INFO: "\033[32m",     # green
    logging.WARNING: "\033[33m",  # yellow
    logging.ERROR: "\033[31m",    # red
    logging.CRITICAL: "\033[1;31m",
}


class ColorFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        message = super().format(record)
        if not sys.stderr.isatty():
            return message
        color = COLORS.get(record.levelno, "")
        return f"{color}{message}{RESET}" if color else message


def configure_logging() -> None:
    level_name = os.getenv("LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)
    handler = logging.StreamHandler()
    handler.setFormatter(
        ColorFormatter("%(asctime)s | %(levelname)-8s | %(name)s | %(message)s", "%H:%M:%S")
    )
    root = logging.getLogger()
    root.setLevel(level)
    # Uvicorn may configure logging before the application imports this
    # module. Replace only our own handler to avoid duplicate application logs.
    if not any(getattr(item, "_trace_handler", False) for item in root.handlers):
        handler._trace_handler = True
        root.addHandler(handler)


logger = logging.getLogger("trace")
