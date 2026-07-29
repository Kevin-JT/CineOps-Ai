import asyncio
import logging
from collections.abc import Awaitable, Callable
from enum import Enum
from typing import Any, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")


class CircuitBreakerState(Enum):
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"


class CircuitBreakerOpenError(Exception):
    """Raised when attempting to execute a call while the circuit breaker is OPEN."""


class CircuitBreaker:
    """
    A generic async Circuit Breaker to prevent cascading failures to external providers.
    """

    def __init__(
        self,
        name: str,
        failure_threshold: int = 5,
        recovery_timeout_sec: float = 60.0,
        expected_exceptions: tuple[type[Exception], ...] = (Exception,),
    ) -> None:
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout_sec = recovery_timeout_sec
        self.expected_exceptions = expected_exceptions

        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.last_failure_time = 0.0

    async def call(
        self, func: Callable[..., Awaitable[T]], *args: Any, **kwargs: Any
    ) -> T:
        """
        Executes the provided async function, tracking failures.
        """
        if self.state == CircuitBreakerState.OPEN:
            if self._is_recovery_time_reached():
                logger.info(f"CircuitBreaker '{self.name}' entering HALF_OPEN state.")
                self.state = CircuitBreakerState.HALF_OPEN
            else:
                raise CircuitBreakerOpenError(f"CircuitBreaker '{self.name}' is OPEN.")

        try:
            result = await func(*args, **kwargs)

            if self.state == CircuitBreakerState.HALF_OPEN:
                logger.info(
                    f"CircuitBreaker '{self.name}' recovered. Entering CLOSED state."
                )
                self._reset()

            return result
        except self.expected_exceptions:
            self._record_failure()
            raise

    def _record_failure(self) -> None:
        self.failure_count += 1
        self.last_failure_time = asyncio.get_event_loop().time()

        if self.state in (
            CircuitBreakerState.CLOSED,
            CircuitBreakerState.HALF_OPEN,
        ) and (
            self.failure_count >= self.failure_threshold
            or self.state == CircuitBreakerState.HALF_OPEN
        ):
            logger.warning(
                f"CircuitBreaker '{self.name}' failure threshold reached. Entering OPEN state."
            )
            self.state = CircuitBreakerState.OPEN

    def _is_recovery_time_reached(self) -> bool:
        current_time = asyncio.get_event_loop().time()
        return (current_time - self.last_failure_time) >= self.recovery_timeout_sec

    def _reset(self) -> None:
        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
