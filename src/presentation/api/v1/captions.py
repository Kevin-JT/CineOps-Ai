from fastapi import APIRouter, Depends

from src.application.services.caption import CaptionGenerationService
from src.domain.models.media_item import MediaItem
from src.presentation.api.dependencies import get_caption_service
from src.presentation.api.dtos.requests import GenerateCaptionRequest
from src.presentation.api.dtos.responses import GeneratedCaptionResponse

router = APIRouter(prefix="/captions", tags=["captions"])


@router.post("/generate", response_model=GeneratedCaptionResponse)
async def generate_caption(
    request: GenerateCaptionRequest,
    service: CaptionGenerationService = Depends(get_caption_service),
) -> GeneratedCaptionResponse:

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

    caption = await service.generate_caption(domain_item)
    return GeneratedCaptionResponse(caption=caption)
