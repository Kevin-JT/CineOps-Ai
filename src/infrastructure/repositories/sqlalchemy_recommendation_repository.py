import json
import uuid
from collections.abc import Sequence

from sqlalchemy import select
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

    def _to_domain(self, db_model: Recommendation) -> RecommendationLog:
        return RecommendationLog(
            prompt=db_model.prompt,
            response=json.dumps(
                db_model.recommendations,
                default=lambda x: x.isoformat() if hasattr(x, "isoformat") else str(x),
            ),
            model=db_model.model,
            response_time=db_model.response_time,
            status=db_model.status,
            id=db_model.id,
            created_at=db_model.created_at,
        )

    async def get(self, id: uuid.UUID) -> RecommendationLog | None:
        async with self._session_factory() as session:
            db_model = await session.get(Recommendation, id)
            if db_model:
                return self._to_domain(db_model)
            return None

    async def get_all(self) -> Sequence[RecommendationLog]:
        async with self._session_factory() as session:
            result = await session.execute(select(Recommendation))
            db_models = result.scalars().all()
            return [self._to_domain(model) for model in db_models]

    async def delete(self, id: uuid.UUID) -> bool:
        async with self._session_factory() as session:
            db_model = await session.get(Recommendation, id)
            if db_model:
                await session.delete(db_model)
                await session.commit()
                return True
            return False
