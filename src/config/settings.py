from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    environment: str = "development"
    tmdb_api_key: str = ""
    gemini_api_key: str = ""
    storage_path: str = "data/storage.json"
    class Config: env_file = ".env"

settings = Settings()
