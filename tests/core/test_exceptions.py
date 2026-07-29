from src.core.exceptions import (
    CineOpsError,
    ConfigurationError,
    ProviderError,
    RepositoryError,
    ValidationError,
)


def test_exception_hierarchy() -> None:
    """Test that all custom exceptions inherit from CineOpsError."""
    assert issubclass(ConfigurationError, CineOpsError)
    assert issubclass(ProviderError, CineOpsError)
    assert issubclass(RepositoryError, CineOpsError)
    assert issubclass(ValidationError, CineOpsError)


def test_exception_raising() -> None:
    """Test that exceptions can be raised and caught correctly."""
    try:
        raise ProviderError("API timeout")
    except CineOpsError as e:
        assert str(e) == "API timeout"
        assert isinstance(e, ProviderError)
