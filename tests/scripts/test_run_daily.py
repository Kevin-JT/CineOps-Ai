from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from scripts.run_daily import run_daily_workflow


@pytest.mark.asyncio
@patch("scripts.run_daily.Container")
async def test_run_daily_workflow_success(mock_container_class: MagicMock) -> None:
    # Arrange
    mock_container = MagicMock()
    mock_coordinator = AsyncMock()

    mock_container.coordinator = mock_coordinator
    mock_container.close = AsyncMock()

    mock_container_class.return_value = mock_container

    # Act
    await run_daily_workflow()

    # Assert
    mock_container_class.assert_called_once()
    mock_coordinator.run_pipeline.assert_awaited_once()
    mock_container.close.assert_awaited_once()


@pytest.mark.asyncio
@patch("scripts.run_daily.sys.exit")
@patch("scripts.run_daily.Container")
async def test_run_daily_workflow_failure(
    mock_container_class: MagicMock, mock_sys_exit: MagicMock
) -> None:
    # Arrange
    mock_container = MagicMock()
    mock_coordinator = AsyncMock()

    # Force failure
    mock_coordinator.run_pipeline.side_effect = Exception("Pipeline failed")

    mock_container.coordinator = mock_coordinator
    mock_container.close = AsyncMock()

    mock_container_class.return_value = mock_container

    # Act
    await run_daily_workflow()

    # Assert
    mock_container_class.assert_called_once()
    mock_coordinator.run_pipeline.assert_awaited_once()
    mock_sys_exit.assert_called_once_with(1)
    mock_container.close.assert_awaited_once()
