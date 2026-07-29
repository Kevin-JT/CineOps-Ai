import json
import logging

from src.core.logger import JSONFormatter, setup_logger


def test_setup_logger_creates_logger() -> None:
    """Test logger initialization."""
    import uuid
    unique_name = f"test_logger_{uuid.uuid4().hex}"
    logger = setup_logger(name=unique_name, log_level="DEBUG", log_dir="/tmp/logs")
    assert logger.name == unique_name
    assert logger.level == logging.DEBUG
    # Should have a StreamHandler and TimedRotatingFileHandler
    assert len(logger.handlers) >= 2


def test_json_formatter() -> None:
    """Test that the custom JSONFormatter produces valid JSON."""
    formatter = JSONFormatter()
    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname="",
        lineno=0,
        msg="Test message",
        args=(),
        exc_info=None,
    )
    
    # Add correlation ID dynamically as it might happen in the app
    record.correlation_id = "12345"

    formatted = formatter.format(record)
    parsed = json.loads(formatted)

    assert parsed["level"] == "INFO"
    assert parsed["component"] == "test"
    assert parsed["message"] == "Test message"
    assert parsed["correlation_id"] == "12345"
    assert "timestamp" in parsed
