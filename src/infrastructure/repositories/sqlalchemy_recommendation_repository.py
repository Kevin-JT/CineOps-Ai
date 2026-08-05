import json
import uuid
from collections.abc import Sequence

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.domain.models.recommendation import RecommendationLog
from src.domain.repositories.recommendation_repository import RecommendationRepository
from src.infrastructure.database.models import Recommendation


class SQLAlchemyRecommendationRepository(RecommendationRepository[RecommendationLog]):
    """
    SQLAlchemy implementation of the RecommendationRepository.
    Converts domain RecommendationLog into the infrastructure model.
    """

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory

    async def create(self, entity: RecommendationLog) -> RecommendationLog:
        # Map domain entity to SQLAlchemy model
        db_model = Recommendation(
            prompt=entity.prompt,
            recommendations=(
                json.loads(entity.response)
                if entity.response and entity.status == "success"
                else {"raw": entity.response}
            ),
            model=entity.model,
            response_time=entity.response_time,
            status=entity.status,
        )

        async with self._session_factory() as session:
            session.add(db_model)
            await session.commit()

        return entity

    async def get(self, id: uuid.UUID) -> RecommendationLog | None:
        # Not heavily used in current flow; left abstract representation
        pass

    async def get_all(self) -> Sequence[RecommendationLog]:
        return []

    async def delete(self, id: uuid.UUID) -> bool:
        return False
