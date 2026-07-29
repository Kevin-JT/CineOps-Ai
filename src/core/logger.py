"""
Structured logging configuration for CineOps AI.
"""

import json
import logging
import os
from datetime import UTC, datetime
from logging.handlers import TimedRotatingFileHandler
from typing import Any


class JSONFormatter(logging.Formatter):
    """
    Custom formatter to output logs in structured JSON format.
    """

    def format(self, record: logging.LogRecord) -> str:
        log_data: dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(record.created, tz=UTC).isoformat(),
            "level": record.levelname,
            "component": record.name,
            "message": record.getMessage(),
        }

        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Include custom correlation ID if it exists
        if hasattr(record, "correlation_id"):
            log_data["correlation_id"] = record.correlation_id

        return json.dumps(log_data)


def setup_logger(
    name: str = "cineops", log_level: str = "INFO", log_dir: str = "logs"
) -> logging.Logger:
    """
    Configures and returns a structured logger.

    Args:
        name: Name of the logger.
        log_level: Logging level (e.g., 'DEBUG', 'INFO').
        log_dir: Directory to store log files.

    Returns:
        Configured logging.Logger instance.
    """
    logger = logging.getLogger(name)

    # Avoid duplicating handlers if already set on this specific logger
    if logger.handlers:
        return logger

    parsed_level = getattr(logging, log_level.upper(), logging.INFO)
    logger.setLevel(parsed_level)

    # Ensure log directory exists
    os.makedirs(log_dir, exist_ok=True)

    json_formatter = JSONFormatter()
    standard_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Console Handler (Standard text)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(parsed_level)
    console_handler.setFormatter(standard_formatter)

    # File Handler (JSON structured, Daily rotating)
    log_file = os.path.join(log_dir, f"{name}.log")
    file_handler = TimedRotatingFileHandler(
        log_file, when="midnight", interval=1, backupCount=30
    )
    file_handler.setLevel(parsed_level)
    file_handler.setFormatter(json_formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger
