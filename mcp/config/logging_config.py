"""
Centralized logging configuration.
Call setup_logging() exactly once, at application startup (from main.py).
All other modules should use logging.getLogger(__name__) and rely on
this configuration - never call basicConfig() elsewhere.
"""

import logging
import sys


LOG_FORMAT = (
    "%(asctime)s | %(levelname)-8s | %(name)s | "
    "request_id=%(request_id)s | %(message)s"
)

DEFAULT_REQUEST_ID = "-"


class RequestIdDefaultFilter(logging.Filter):
    """
    Ensures every log record has a request_id attribute, even for logs
    emitted outside the request/response cycle (e.g. at startup).
    Prevents KeyError in the formatter when request_id hasn't been
    attached by the logging middleware yet.
    """

    def filter(self, record: logging.LogRecord) -> bool:
        if not hasattr(record, "request_id"):
            record.request_id = DEFAULT_REQUEST_ID
        return True


def setup_logging(log_level: str = "INFO") -> None:
    """
    Configures the root logger with a consistent format, a stdout
    handler, and a filter guaranteeing request_id is always present.
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level.upper())

    # Avoid duplicate handlers if setup_logging is called more than once
    # (e.g. in tests that call create_app() multiple times).
    if root_logger.handlers:
        root_logger.handlers.clear()

    handler = logging.StreamHandler(stream=sys.stdout)
    handler.setFormatter(logging.Formatter(LOG_FORMAT))
    handler.addFilter(RequestIdDefaultFilter())

    root_logger.addHandler(handler)