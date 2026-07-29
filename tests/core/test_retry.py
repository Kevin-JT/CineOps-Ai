import pytest

from src.core.exceptions import CineOpsError
from src.core.retry import async_retry


@pytest.mark.asyncio
async def test_async_retry_success_first_try() -> None:
    """Test that retry decorator works on successful calls without retrying."""
    attempts = 0

    @async_retry(max_attempts=3, base_delay=0.01)
    async def successful_func() -> str:
        nonlocal attempts
        attempts += 1
        return "success"

    result = await successful_func()
    assert result == "success"
    assert attempts == 1


@pytest.mark.asyncio
async def test_async_retry_success_after_failure() -> None:
    """Test that retry decorator succeeds after an initial failure."""
    attempts = 0

    @async_retry(max_attempts=3, base_delay=0.01, exceptions=(ValueError,))
    async def flaky_func() -> str:
        nonlocal attempts
        attempts += 1
        if attempts < 2:
            raise ValueError("Temporary failure")
        return "success"

    result = await flaky_func()
    assert result == "success"
    assert attempts == 2


@pytest.mark.asyncio
async def test_async_retry_max_attempts_exceeded() -> None:
    """Test that retry decorator raises CineOpsError after max attempts."""
    attempts = 0

    @async_retry(max_attempts=2, base_delay=0.01, exceptions=(ValueError,))
    async def failing_func() -> str:
        nonlocal attempts
        attempts += 1
        raise ValueError("Permanent failure")

    with pytest.raises(CineOpsError) as exc_info:
        await failing_func()

    assert attempts == 2
    assert "Operation failing_func failed after 2 attempts" in str(exc_info.value)
