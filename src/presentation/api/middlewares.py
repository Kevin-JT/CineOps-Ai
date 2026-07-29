import logging
import time
import uuid
from collections.abc import Awaitable, Callable
from typing import Any

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from src.core.context import correlation_id_ctx

logger = logging.getLogger(__name__)


class RequestTimingMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        start_time = time.perf_counter()
        response = await call_next(request)
        process_time = time.perf_counter() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        return response


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
        token = correlation_id_ctx.set(correlation_id)

        try:
            logger.info(f"[{correlation_id}] {request.method} {request.url.path}")
            response = await call_next(request)
            response.headers["X-Correlation-ID"] = correlation_id
            return response
        finally:
            correlation_id_ctx.reset(token)


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(
        self, app: Any, max_requests: int = 100, window_seconds: int = 60
    ) -> None:
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._requests: dict[str, list[float]] = {}

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        client_ip = request.client.host if request.client else "unknown"
        now = time.time()

        client_reqs = self._requests.get(client_ip, [])
        client_reqs = [t for t in client_reqs if t > now - self.window_seconds]

        if len(client_reqs) >= self.max_requests:
            from fastapi import status
            from fastapi.responses import JSONResponse

            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={"detail": "Too many requests. Please try again later."},
            )

        client_reqs.append(now)
        self._requests[client_ip] = client_reqs

        return await call_next(request)
