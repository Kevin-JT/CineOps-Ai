from fastapi import APIRouter, Depends, HTTPException, status

from src.application.services.auth import AuthService
from src.core.exceptions import CineOpsError
from src.presentation.api.dependencies import get_auth_service
from src.presentation.api.dtos.auth import (
    RefreshTokenRequest,
    TokenResponse,
    UserCredentialsRequest,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED
)
async def register(
    request: UserCredentialsRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    """
    Register a new user and return tokens.
    """
    try:
        user = await auth_service.register(request.email, request.password)
        access_token = auth_service.create_access_token(user.email)
        refresh_token = auth_service.create_refresh_token(user.email)
        return TokenResponse(access_token=access_token, refresh_token=refresh_token)
    except CineOpsError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.post("/login", response_model=TokenResponse)
async def login(
    request: UserCredentialsRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    """
    Authenticate a user and return tokens.
    """
    user = await auth_service.authenticate(request.email, request.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    access_token = auth_service.create_access_token(user.email)
    refresh_token = auth_service.create_refresh_token(user.email)
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    request: RefreshTokenRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    """
    Issue a new access token using a refresh token.
    """
    try:
        access_token = await auth_service.refresh_access_token(request.refresh_token)
        return TokenResponse(
            access_token=access_token,
            refresh_token=request.refresh_token,
        )
    except CineOpsError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
