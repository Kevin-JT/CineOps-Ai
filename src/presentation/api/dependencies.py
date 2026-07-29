from fastapi import HTTPException, Request, Security, status
from fastapi.security import APIKeyHeader

from src.application.services.caption import CaptionGenerationService
from src.application.services.coordinator import WorkflowCoordinator
from src.application.services.hashtag import HashtagGenerationService
from src.application.services.recommendation import RecommendationService
from src.core.di import Container

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def get_container(request: Request) -> Container:
    """
    Retrieves the global DI container from the FastAPI app state.
    """
    return request.app.state.container  # type: ignore


def verify_api_key(
    request: Request, api_key_header: str = Security(api_key_header)
) -> str:
    """
    Validates that the provided API key matches the configured secret.
    """
    container = get_container(request)
    if api_key_header == container.settings.api_key_secret:
        return api_key_header
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN, detail="Could not validate credentials"
    )


def get_recommendation_service(request: Request) -> RecommendationService:
    return get_container(request).recommendation_service


def get_caption_service(request: Request) -> CaptionGenerationService:
    return get_container(request).caption_service


def get_hashtag_service(request: Request) -> HashtagGenerationService:
    return get_container(request).hashtag_service


def get_coordinator(request: Request) -> WorkflowCoordinator:
    return get_container(request).coordinator
