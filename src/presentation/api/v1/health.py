from fastapi import APIRouter, Depends

from src.core.di import Container
from src.presentation.api.dependencies import get_container
from src.presentation.api.dtos.health import DependencyHealth, HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    return HealthResponse(status="ok", version="0.1.0")


@router.get("/ready", response_model=DependencyHealth)
async def readiness_check(
    container: Container = Depends(get_container),
) -> DependencyHealth:
    return DependencyHealth(
        status="ready",
        tmdb_configured=bool(container.settings.tmdb_api_key),
        tmdb_cb_state=container.tmdb_cb.state.value,
        jikan_configured=True,  # No auth needed for Jikan currently
        jikan_cb_state=container.jikan_cb.state.value,
        gemini_configured=bool(container.settings.gemini_api_key),
        gemini_cb_state=container.gemini_cb.state.value,
        telegram_configured=bool(container.settings.telegram_bot_token),
        telegram_cb_state=container.telegram_cb.state.value,
    )


@router.get("/version")
async def version() -> dict[str, str]:
    return {"version": "0.1.0"}
