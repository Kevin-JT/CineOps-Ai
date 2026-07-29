from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    version: str


class DependencyHealth(BaseModel):
    status: str
    tmdb_configured: bool
    jikan_configured: bool
    gemini_configured: bool
    telegram_configured: bool
