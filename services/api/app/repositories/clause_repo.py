import uuid
from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.clause import Clause

class ClauseRepo:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_contract(self, contract_id: uuid.UUID) -> List[Clause]:
        result = await self.db.execute(
            select(Clause).where(Clause.contract_id == contract_id).order_by(Clause.position_index.asc())
        )
        return list(result.scalars().all())

    async def bulk_create(self, clauses: List[Clause]) -> List[Clause]:
        self.db.add_all(clauses)
        await self.db.commit()
        for c in clauses:
            await self.db.refresh(c)
        return clauses

    async def delete_by_contract(self, contract_id: uuid.UUID) -> None:
        clauses = await self.get_by_contract(contract_id)
        for c in clauses:
            await self.db.delete(c)
        await self.db.commit()
