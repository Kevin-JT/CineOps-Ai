"""
Structured logging configuration for CineOps AI.
"""

import json
import logging
from datetime import UTC, datetime
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
from typing import Any

from src.core.context import get_correlation_id, get_execution_id


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

        # Include correlation ID from context if it exists
        correlation_id = get_correlation_id()
        if correlation_id:
            log_data["correlation_id"] = correlation_id
        # Include custom correlation ID if it exists on record (fallback)
        elif hasattr(record, "correlation_id"):
            log_data["correlation_id"] = record.correlation_id

        # Include execution ID from context if it exists
        execution_id = get_execution_id()
        if execution_id:
            log_data["execution_id"] = execution_id

        return json.dumps(
            log_data,
            default=lambda x: x.isoformat() if hasattr(x, "isoformat") else str(x),
        )


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
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)

    json_formatter = JSONFormatter()

    class ConsoleFormatter(logging.Formatter):
        def format(self, record: logging.LogRecord) -> str:
            from src.core.context import get_correlation_id

            corr_id = get_correlation_id()
            prefix = f"[{corr_id}] " if corr_id else ""
            record.msg = f"{prefix}{record.msg}"
            return super().format(record)

    standard_formatter = ConsoleFormatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Console Handler (Standard text)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(parsed_level)
    console_handler.setFormatter(standard_formatter)

    # File Handler (JSON structured, Daily rotating)
    log_file = log_path / f"{name}.log"
    file_handler = TimedRotatingFileHandler(
        str(log_file), when="midnight", interval=1, backupCount=30
    )
    file_handler.setLevel(parsed_level)
    file_handler.setFormatter(json_formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger
