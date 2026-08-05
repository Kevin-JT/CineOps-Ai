from fastapi import Depends, HTTPException, Request, Security, status
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


from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.application.services.auth import AuthService
from src.domain.models.user import User

bearer_scheme = HTTPBearer(auto_error=False)


def get_auth_service(request: Request) -> AuthService:
    return get_container(request).auth_service


async def get_current_user(
    request: Request,
    auth_service: AuthService = Depends(get_auth_service),
    token: HTTPAuthorizationCredentials | None = Security(bearer_scheme),
) -> User:
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = await auth_service.get_user_from_token(token.credentials)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or token invalid",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user
