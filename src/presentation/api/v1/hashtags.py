from fastapi import APIRouter, Depends

from src.application.services.hashtag import HashtagGenerationService
from src.domain.models.media_item import MediaItem
from src.presentation.api.dependencies import get_hashtag_service
from src.presentation.api.dtos.requests import GenerateHashtagsRequest
from src.presentation.api.dtos.responses import GeneratedHashtagsResponse

router = APIRouter(prefix="/hashtags", tags=["hashtags"])


@router.post("/generate", response_model=GeneratedHashtagsResponse)
async def generate_hashtags(
    request: GenerateHashtagsRequest,
    service: HashtagGenerationService = Depends(get_hashtag_service),
) -> GeneratedHashtagsResponse:

    item = request.item
    domain_item = MediaItem(
        id=item.id,
        title=item.title,
        overview=item.overview,
        media_type=item.media_type,
        release_date=item.release_date,
        rating=item.rating,
        popularity=item.popularity,
        genres=item.genres,
    )

    hashtags = await service.generate_hashtags(domain_item)
    return GeneratedHashtagsResponse(hashtags=hashtags)
