import logging

from fastapi import Request, status
from fastapi.responses import JSONResponse

from src.core.exceptions import CineOpsError, ProviderError

logger = logging.getLogger(__name__)


async def cineops_error_handler(request: Request, exc: CineOpsError) -> JSONResponse:
    """
    Catches any application-level errors and converts them to HTTP 400.
    """
    logger.error(f"Application error on {request.url.path}: {exc}")
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": str(exc), "type": "application_error"},
    )


async def provider_error_handler(request: Request, exc: ProviderError) -> JSONResponse:
    """
    Catches any external provider errors and converts them to HTTP 502 Bad Gateway.
    """
    logger.error(f"Provider error on {request.url.path}: {exc}")
    return JSONResponse(
        status_code=status.HTTP_502_BAD_GATEWAY,
        content={
            "detail": "Failed to communicate with an external provider.",
            "type": "provider_error",
        },
    )


async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Catches any unhandled exceptions to prevent the server from crashing.
    """
    logger.critical(f"Unhandled exception on {request.url.path}: {exc}", exc_info=exc)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An internal server error occurred."},
    )
