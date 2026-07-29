from datetime import datetime

from pydantic import BaseModel, Field


class MediaItem(BaseModel):
    id: str
    title: str
    overview: str
    media_type: str = Field(..., description="movie, tv, or anime")
    release_date: str | None = None
    rating: float = 0.0
    genres: list[str] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
