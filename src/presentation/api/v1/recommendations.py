from fastapi import APIRouter, Depends

from src.application.services.recommendation import RecommendationService
from src.domain.models.media_item import MediaItem
from src.presentation.api.dependencies import get_recommendation_service
from src.presentation.api.dtos.requests import GenerateRecommendationRequest
from src.presentation.api.dtos.responses import (
    MediaItemResponse,
    RecommendationResponse,
)

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@router.post("/generate", response_model=RecommendationResponse)
async def generate_recommendations(
    request: GenerateRecommendationRequest,
    service: RecommendationService = Depends(get_recommendation_service),
) -> RecommendationResponse:

    # Map request DTO to Domain models
    domain_items = [
        MediaItem(
            id=item.id,
            title=item.title,
            overview=item.overview,
            media_type=item.media_type,
            release_date=item.release_date,
            rating=item.rating,
            popularity=item.popularity,
            genres=item.genres,
        )
        for item in request.items
    ]

    domain_recommendation = await service.generate_recommendation(domain_items)

    # Map Domain model back to Response DTO (Clean Architecture)
    return RecommendationResponse(
        id=domain_recommendation.id,
        items=[
            MediaItemResponse(
                id=i.id,
                title=i.title,
                overview=i.overview,
                media_type=i.media_type,
                release_date=i.release_date,
                rating=i.rating,
                popularity=i.popularity,
                genres=i.genres,
            )
            for i in domain_recommendation.items
        ],
        target_audience=domain_recommendation.target_audience,
        reasoning=domain_recommendation.reasoning,
        viral_score=domain_recommendation.viral_score,
        generated_at=domain_recommendation.generated_at,
    )
