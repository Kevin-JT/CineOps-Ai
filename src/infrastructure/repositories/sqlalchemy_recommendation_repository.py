import uuid
from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.repositories.recommendation_repository import RecommendationRepository
from src.infrastructure.database.models import Recommendation


class SQLAlchemyRecommendationRepository(RecommendationRepository[Recommendation]):
    """
    SQLAlchemy implementation of the RecommendationRepository.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, entity: Recommendation) -> Recommendation:
        self._session.add(entity)
        await self._session.commit()
        await self._session.refresh(entity)
        return entity

    async def get(self, id: uuid.UUID) -> Recommendation | None:
        return await self._session.get(Recommendation, id)

    async def get_all(self) -> Sequence[Recommendation]:
        result = await self._session.execute(select(Recommendation))
        return result.scalars().all()

    async def delete(self, id: uuid.UUID) -> bool:
        entity = await self.get(id)
        if entity:
            await self._session.delete(entity)
            await self._session.commit()
            return True
        return False
