from pydantic_settings import BaseSettings, SettingsConfigDict

from src.config.environments import Environment


class Settings(BaseSettings):
    """
    Application configuration managed by Pydantic.
    Values are automatically loaded from environment variables or a .env file.
    """

    app_env: Environment = Environment.DEVELOPMENT
    log_level: str = "INFO"

    # API Keys (Secrets)
    tmdb_api_key: str = ""
    gemini_api_key: str = ""
    telegram_bot_token: str = ""
    telegram_chat_id: str = ""

    # Infrastructure
    jikan_base_url: str = "https://api.jikan.moe/v4"
    data_directory: str = "data"
    storage_path: str = "data/storage.json"
    cache_path: str = "data/cache.json"

    # Settings Configuration
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


def get_settings() -> Settings:
    """
    Factory function to retrieve application settings.
    """
    return Settings()


settings = get_settings()
