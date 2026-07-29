from pydantic import BaseModel, ConfigDict, Field


class MediaItemRequest(BaseModel):
    """
    Representation of a MediaItem used in API requests.
    """

    id: str = Field(..., min_length=1, max_length=100)
    title: str = Field(..., min_length=1, max_length=300)
    overview: str = Field(default="", max_length=2000)
    media_type: str = Field(
        ..., pattern="^(movie|tv|anime)$", description="movie, tv, or anime"
    )
    release_date: str | None = None
    rating: float = Field(0.0, ge=0.0, le=10.0)
    popularity: float = Field(0.0, ge=0.0)
    genres: list[str] = Field(default_factory=list, max_length=20)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "tt1375666",
                "title": "Inception",
                "overview": "A thief who steals corporate secrets through the use of dream-sharing technology...",
                "media_type": "movie",
                "release_date": "2010-07-16",
                "rating": 8.8,
                "popularity": 150.43,
                "genres": ["Action", "Sci-Fi", "Thriller"],
            }
        }
    )


class GenerateRecommendationRequest(BaseModel):
    items: list[MediaItemRequest] = Field(..., min_length=1, max_length=50)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "items": [
                    {
                        "id": "tt1375666",
                        "title": "Inception",
                        "overview": "A thief who steals corporate secrets...",
                        "media_type": "movie",
                        "release_date": "2010-07-16",
                        "rating": 8.8,
                        "popularity": 150.43,
                        "genres": ["Action", "Sci-Fi", "Thriller"],
                    }
                ]
            }
        }
    )


class GenerateCaptionRequest(BaseModel):
    item: MediaItemRequest

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "item": {
                    "id": "tt1375666",
                    "title": "Inception",
                    "overview": "A thief who steals corporate secrets...",
                    "media_type": "movie",
                    "release_date": "2010-07-16",
                    "rating": 8.8,
                    "popularity": 150.43,
                    "genres": ["Action", "Sci-Fi", "Thriller"],
                }
            }
        }
    )


class GenerateHashtagsRequest(BaseModel):
    item: MediaItemRequest

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "item": {
                    "id": "tt1375666",
                    "title": "Inception",
                    "overview": "A thief who steals corporate secrets...",
                    "media_type": "movie",
                    "release_date": "2010-07-16",
                    "rating": 8.8,
                    "popularity": 150.43,
                    "genres": ["Action", "Sci-Fi", "Thriller"],
                }
            }
        }
    )
