"""
Retry utility with exponential backoff for network operations.
"""

import asyncio
import logging
from collections.abc import Callable, Coroutine
from functools import wraps
from typing import Any, TypeVar

from src.config import constants
from src.core.exceptions import CineOpsError

logger = logging.getLogger(__name__)

T = TypeVar("T")


def async_retry(
    max_attempts: int = constants.MAX_RETRIES,
    base_delay: float = constants.RETRY_BASE_DELAY_SEC,
    max_delay: float = constants.RETRY_MAX_DELAY_SEC,
    exceptions: tuple[type[Exception], ...] = (Exception,),
    raise_exc: type[Exception] = CineOpsError,
) -> Callable[..., Any]:
    """
    Decorator for retrying async functions with exponential backoff.

    Args:
        max_attempts: Maximum number of retry attempts.
        base_delay: Initial delay in seconds.
        max_delay: Maximum delay between retries.
        exceptions: Tuple of exceptions to catch and retry on.
    """

    def decorator(
        func: Callable[..., Coroutine[Any, Any, T]],
    ) -> Callable[..., Coroutine[Any, Any, T]]:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> T:
            attempt = 1
            delay = base_delay

            while attempt <= max_attempts:
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_attempts:
                        logger.error(
                            f"Final attempt {attempt}/{max_attempts} failed for {func.__name__}: {e!s}"
                        )
                        raise raise_exc(
                            f"Operation {func.__name__} failed after {max_attempts} attempts: {e!s}"
                        ) from e

                    logger.warning(
                        f"Attempt {attempt}/{max_attempts} failed for {func.__name__}: {e!s}. "
                        f"Retrying in {delay:.2f} seconds..."
                    )
                    await asyncio.sleep(delay)
                    attempt += 1
                    delay = min(delay * 2, max_delay)

            # This line should logically never be reached due to the `raise` above, but satisfies MyPy.
            raise raise_exc(f"Operation {func.__name__} failed.")

        return wrapper

    return decorator
