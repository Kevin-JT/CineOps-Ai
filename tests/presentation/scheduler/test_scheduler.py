import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.core.exceptions import CineOpsError
from src.presentation.scheduler.engine import BackgroundScheduler
from src.presentation.scheduler.jobs import WorkflowJob


@pytest.fixture
def mock_container() -> MagicMock:
    container = MagicMock()
    container.coordinator = AsyncMock()
    return container


@pytest.fixture
def mock_settings() -> MagicMock:
    settings = MagicMock()
    settings.scheduler_interval_seconds = 0.1  # Fast for tests
    return settings


@pytest.mark.asyncio
async def test_workflow_job_success(mock_container: MagicMock) -> None:
    job = WorkflowJob(mock_container)
    await job.execute()
    mock_container.coordinator.run_pipeline.assert_called_once()


@pytest.mark.asyncio
async def test_workflow_job_retries_on_failure(mock_container: MagicMock) -> None:
    # Make the pipeline fail twice, then succeed
    mock_container.coordinator.run_pipeline.side_effect = [
        Exception("Temp Error 1"),
        Exception("Temp Error 2"),
        None,
    ]
    job = WorkflowJob(mock_container)

    # We patch the delay to speed up the test
    with patch("asyncio.sleep", new_callable=AsyncMock):
        await job.execute()

    assert mock_container.coordinator.run_pipeline.call_count == 3


@pytest.mark.asyncio
async def test_workflow_job_fails_after_max_retries(mock_container: MagicMock) -> None:
    mock_container.coordinator.run_pipeline.side_effect = Exception("Fatal Error")
    job = WorkflowJob(mock_container)

    with (
        patch("asyncio.sleep", new_callable=AsyncMock),
        pytest.raises(CineOpsError, match="Operation execute failed"),
    ):
        await job.execute()

    assert mock_container.coordinator.run_pipeline.call_count == 3


@pytest.mark.asyncio
async def test_background_scheduler_execution_and_stop(
    mock_settings: MagicMock,
) -> None:
    scheduler = BackgroundScheduler(mock_settings)

    job_func = AsyncMock()

    task = scheduler.start(job_func)

    # Wait long enough for the loop to execute at least once (interval is 0.1)
    await asyncio.sleep(0.15)

    await scheduler.stop()
    await task  # Ensure task is fully cleaned up

    assert job_func.call_count >= 1
    assert scheduler.stop_event.is_set()


@pytest.mark.asyncio
async def test_background_scheduler_catches_unhandled_exceptions(
    mock_settings: MagicMock,
) -> None:
    scheduler = BackgroundScheduler(mock_settings)

    job_func = AsyncMock()
    job_func.side_effect = Exception("Unhandled loop error")

    task = scheduler.start(job_func)

    # Wait for execution
    await asyncio.sleep(0.15)

    # The loop should NOT have crashed, it should continue running and hit the sleep
    assert not task.done()

    await scheduler.stop()
    await task

    assert job_func.call_count >= 1
