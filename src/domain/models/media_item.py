from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class MediaItem(BaseModel):
    id: str
    title: str
    overview: str
    media_type: str = Field(..., description="movie, tv, or anime")
    release_date: Optional[str] = None
    rating: float = 0.0
    genres: List[str] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
