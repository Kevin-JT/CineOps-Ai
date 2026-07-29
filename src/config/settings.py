from functools import lru_cache

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from src.config.environments import Environment


class Settings(BaseSettings):
    """
    Application configuration managed by Pydantic.
    Values are automatically loaded from environment variables or a .env file.
    """

    app_env: Environment = Environment.DEVELOPMENT
    log_level: str = "INFO"

    # Internal API Security
    api_key_secret: str = "change-me-in-production"

    # API Keys (Secrets)
    tmdb_api_key: str
    gemini_api_key: str
    telegram_bot_token: str
    telegram_chat_id: str

    # Infrastructure
    jikan_base_url: str = "https://api.jikan.moe/v4"
    data_directory: str = "data"
    storage_path: str = "data/storage.json"
    cache_path: str = "data/cache.json"
    cache_ttl_seconds: int = 3600  # Default to 1 hour

    # Scheduler
    scheduler_enabled: bool = False
    scheduler_interval_seconds: int = 86400  # Default to once a day (24 hours)

    # Database
    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/cineops"

    # Settings Configuration
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @model_validator(mode="after")
    def validate_production_secrets(self) -> "Settings":
        if (
            self.app_env == Environment.PRODUCTION
            and self.api_key_secret == "change-me-in-production"
        ):
            raise ValueError("api_key_secret must be changed in production")
        return self


@lru_cache
def get_settings() -> Settings:
    """
    Factory function to retrieve application settings.
    """
    return Settings()  # type: ignore
