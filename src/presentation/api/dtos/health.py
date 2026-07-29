from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    version: str


class DependencyHealth(BaseModel):
    status: str
    tmdb_configured: bool
    tmdb_cb_state: str
    jikan_configured: bool
    jikan_cb_state: str
    gemini_configured: bool
    gemini_cb_state: str
    telegram_configured: bool
    telegram_cb_state: str
