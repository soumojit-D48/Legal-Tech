import uuid
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.precedent_match import PrecedentMatch

class PrecedentRepo:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_clause(self, clause_id: uuid.UUID) -> Optional[PrecedentMatch]:
        result = await self.db.execute(
            select(PrecedentMatch).where(PrecedentMatch.clause_id == clause_id)
        )
        return result.scalar_one_or_none()

    async def create(self, **kwargs) -> PrecedentMatch:
        match = PrecedentMatch(**kwargs)
        self.db.add(match)
        await self.db.commit()
        await self.db.refresh(match)
        return match
