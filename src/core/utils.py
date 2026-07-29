"""
Shared utilities for the CineOps AI application.
"""

import json
import os
from typing import Any


def ensure_directory(path: str) -> None:
    """
    Ensures that a directory exists, creating it if necessary.
    """
    os.makedirs(path, exist_ok=True)


def safe_json_loads(data: str, default: Any = None) -> Any:
    """
    Safely load JSON data without throwing exceptions.
    Returns default value if parsing fails.
    """
    try:
        return json.loads(data)
    except (json.JSONDecodeError, TypeError):
        return default if default is not None else {}
