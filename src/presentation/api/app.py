import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from src.core.di import Container
from src.core.exceptions import CineOpsError, ProviderError
from src.presentation.api.exceptions import (
    cineops_error_handler,
    global_exception_handler,
    provider_error_handler,
)
from src.presentation.api.middlewares import (
    CorrelationIdMiddleware,
    RateLimitMiddleware,
    RequestTimingMiddleware,
)
from src.presentation.api.v1.router import api_router

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifecycle manager.
    Initializes the dependency injection container on startup and tears it down on shutdown.
    """
    logger.info("Initializing CineOps AI API...")
    app.state.container = Container()
    yield
    logger.info("Shutting down CineOps AI API...")
    await app.state.container.close()


def create_app() -> FastAPI:
    """
    Factory function to create the FastAPI application instance.
    """
    tags_metadata = [
        {"name": "health", "description": "System health and readiness endpoints."},
        {
            "name": "recommendations",
            "description": "Recommendation generation endpoints.",
        },
        {"name": "captions", "description": "Caption generation endpoints."},
        {"name": "hashtags", "description": "Hashtag generation endpoints."},
        {"name": "workflow", "description": "Background workflow orchestration."},
        {"name": "metrics", "description": "Application telemetry and metrics."},
    ]

    app = FastAPI(
        title="CineOps AI API",
        version="1.0.0",
        description="AI-driven cinematic operations and automation system API.",
        openapi_tags=tags_metadata,
        lifespan=lifespan,
    )

    # API Routers
    app.include_router(api_router, prefix="/api/v1")

    # Exception Handlers
    app.add_exception_handler(CineOpsError, cineops_error_handler)  # type: ignore
    app.add_exception_handler(ProviderError, provider_error_handler)  # type: ignore
    app.add_exception_handler(Exception, global_exception_handler)

    # Middlewares (Added in reverse order of execution. Last added = First executed)

    # 5. Closest to Route: Request Timing
    app.add_middleware(RequestTimingMiddleware)

    # 4. Correlation ID Tracking
    app.add_middleware(CorrelationIdMiddleware)

    # 3. Rate Limiting
    app.add_middleware(RateLimitMiddleware, max_requests=100, window_seconds=60)

    # 2. Response Compression
    app.add_middleware(GZipMiddleware, minimum_size=1000)

    # 2. CORS handling (allow_credentials must be False if origins='*')
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 1. Outermost (First executed): Trusted Host
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])

    return app
