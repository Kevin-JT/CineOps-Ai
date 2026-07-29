import os

from src.core.utils import ensure_directory, safe_json_loads


def test_ensure_directory(tmp_path: str) -> None:
    """Test that directory is created correctly."""
    test_dir = os.path.join(tmp_path, "test_dir")
    ensure_directory(test_dir)
    assert os.path.isdir(test_dir)

    # Second call should not raise an exception (exist_ok=True)
    ensure_directory(test_dir)


def test_safe_json_loads() -> None:
    """Test safe json loading behavior."""
    valid_json = '{"key": "value"}'
    invalid_json = "{key: value}"

    # Valid JSON
    assert safe_json_loads(valid_json) == {"key": "value"}

    # Invalid JSON should return default empty dict
    assert safe_json_loads(invalid_json) == {}

    # Invalid JSON with custom default
    assert safe_json_loads(invalid_json, default=[]) == []

    # None input
    assert safe_json_loads(None) == {}  # type: ignore
