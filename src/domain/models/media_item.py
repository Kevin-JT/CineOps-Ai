from datetime import UTC, datetime

from pydantic import BaseModel, ConfigDict, Field


class MediaItem(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: str
    title: str
    overview: str
    media_type: str = Field(..., description="movie, tv, or anime")
    release_date: str | None = None
    rating: float = 0.0
    popularity: float = 0.0
    genres: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
