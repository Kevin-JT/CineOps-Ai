import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.models.recommendation import RecommendationLog
from src.infrastructure.database.models import Recommendation
from src.infrastructure.repositories.sqlalchemy_recommendation_repository import (
    SQLAlchemyRecommendationRepository,
)


@pytest.fixture
def mock_session() -> AsyncMock:
    return AsyncMock(spec=AsyncSession)


@pytest.fixture
def mock_session_factory(mock_session: AsyncMock) -> MagicMock:
    # A context manager factory that yields the mock session
    factory = MagicMock()
    factory.return_value.__aenter__.return_value = mock_session
    return factory


@pytest.fixture
def repository(mock_session_factory: MagicMock) -> SQLAlchemyRecommendationRepository:
    return SQLAlchemyRecommendationRepository(mock_session_factory)


@pytest.mark.asyncio
async def test_create_recommendation_log(
    repository: SQLAlchemyRecommendationRepository, mock_session: AsyncMock
) -> None:
    log = RecommendationLog(
        prompt="prompt",
        response='{"test": 1}',
        model="gemini",
        response_time=0.1,
        status="success",
    )

    result = await repository.create(log)

    assert result == log
    mock_session.add.assert_called_once()
    added_model = mock_session.add.call_args[0][0]
    assert isinstance(added_model, Recommendation)
    assert added_model.prompt == "prompt"
    assert added_model.recommendations == {"test": 1}
    mock_session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_recommendation_log(
    repository: SQLAlchemyRecommendationRepository, mock_session: AsyncMock
) -> None:
    uid = uuid.uuid4()
    mock_db_model = Recommendation(
        id=uid,
        prompt="p",
        recommendations={},
        model="m",
        response_time=1.0,
        status="s",
    )
    mock_session.get.return_value = mock_db_model

    result = await repository.get(uid)

    assert result is not None
    assert result.id == uid
    assert result.prompt == "p"
    mock_session.get.assert_awaited_once_with(Recommendation, uid)


@pytest.mark.asyncio
async def test_get_all_recommendation_logs(
    repository: SQLAlchemyRecommendationRepository, mock_session: AsyncMock
) -> None:
    uid = uuid.uuid4()
    mock_db_model = Recommendation(
        id=uid,
        prompt="p",
        recommendations={},
        model="m",
        response_time=1.0,
        status="s",
    )

    mock_result = MagicMock()
    mock_result.scalars().all.return_value = [mock_db_model]
    mock_session.execute.return_value = mock_result

    result = await repository.get_all()

    assert len(result) == 1
    assert result[0].id == uid
    mock_session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_recommendation_log(
    repository: SQLAlchemyRecommendationRepository, mock_session: AsyncMock
) -> None:
    uid = uuid.uuid4()
    mock_db_model = Recommendation(
        id=uid,
        prompt="p",
        recommendations={},
        model="m",
        response_time=1.0,
        status="s",
    )
    mock_session.get.return_value = mock_db_model

    result = await repository.delete(uid)

    assert result is True
    mock_session.delete.assert_awaited_once_with(mock_db_model)
    mock_session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_recommendation_log_not_found(
    repository: SQLAlchemyRecommendationRepository, mock_session: AsyncMock
) -> None:
    mock_session.get.return_value = None
    result = await repository.delete(uuid.uuid4())
    assert result is False
    mock_session.delete.assert_not_called()
