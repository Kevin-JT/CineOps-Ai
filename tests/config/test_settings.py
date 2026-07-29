import os

from src.config.environments import Environment
from src.config.settings import Settings, get_settings


def test_settings_default_values() -> None:
    """Test that settings load with correct defaults when no env vars are set."""
    # Ensure no relevant env vars are polluting the test
    os.environ.pop("APP_ENV", None)
    
    settings = Settings()
    assert settings.app_env == Environment.DEVELOPMENT
    assert settings.log_level == "INFO"
    assert settings.jikan_base_url == "https://api.jikan.moe/v4"
    assert settings.data_directory == "data"


def test_get_settings_singleton_like_behavior() -> None:
    """Test that get_settings() returns a Settings instance."""
    settings = get_settings()
    assert isinstance(settings, Settings)
