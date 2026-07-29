from datetime import datetime

from pydantic import BaseModel, ConfigDict


class GeneratedCaptionResponse(BaseModel):
    caption: str

    model_config = ConfigDict(
        json_schema_extra={
            "example": {"caption": "Dive into the mind-bending world of dreams! 🌀💤"}
        }
    )


class GeneratedHashtagsResponse(BaseModel):
    hashtags: list[str]

    model_config = ConfigDict(
        json_schema_extra={
            "example": {"hashtags": ["#SciFi", "#MindBender", "#MustWatch", "#Nolan"]}
        }
    )


class MediaItemResponse(BaseModel):
    id: str
    title: str
    overview: str
    media_type: str
    release_date: str | None
    rating: float
    popularity: float
    genres: list[str]

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "tt0816692",
                "title": "Interstellar",
                "overview": "A team of explorers travel through a wormhole in space...",
                "media_type": "movie",
                "release_date": "2014-11-05",
                "rating": 8.7,
                "popularity": 120.5,
                "genres": ["Adventure", "Drama", "Sci-Fi"],
            }
        }
    )


class RecommendationResponse(BaseModel):
    id: str
    items: list[MediaItemResponse]
    target_audience: str
    reasoning: str
    viral_score: float
    generated_at: datetime

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "rec-12345",
                "items": [
                    {
                        "id": "tt0816692",
                        "title": "Interstellar",
                        "overview": "A team of explorers travel through a wormhole in space...",
                        "media_type": "movie",
                        "release_date": "2014-11-05",
                        "rating": 8.7,
                        "popularity": 120.5,
                        "genres": ["Adventure", "Drama", "Sci-Fi"],
                    }
                ],
                "target_audience": "Fans of cerebral sci-fi and Christopher Nolan.",
                "reasoning": "Because you liked Inception, you might enjoy this other masterpiece.",
                "viral_score": 9.2,
                "generated_at": "2026-07-29T12:00:00Z",
            }
        }
    )
