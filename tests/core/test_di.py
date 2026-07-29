from src.config.settings import Settings
from src.core.di import Container


def test_container_initialization() -> None:
    """Test that the DI Container initializes correctly and loads settings."""
    container = Container()
    assert container.settings is not None
    assert isinstance(container.settings, Settings)
