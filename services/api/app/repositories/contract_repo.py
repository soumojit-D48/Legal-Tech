import uuid
from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.contract import Contract

class ContractRepo:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, contract_id: uuid.UUID) -> Optional[Contract]:
        result = await self.db.execute(select(Contract).where(Contract.id == contract_id))
        return result.scalar_one_or_none()

    async def get_all_by_user(self, user_id: uuid.UUID) -> List[Contract]:
        result = await self.db.execute(
            select(Contract).where(Contract.user_id == user_id).order_by(Contract.created_at.desc())
        )
        return list(result.scalars().all())

    async def create(self, **kwargs) -> Contract:
        contract = Contract(**kwargs)
        self.db.add(contract)
        await self.db.commit()
        await self.db.refresh(contract)
        return contract

    async def update(self, contract: Contract) -> Contract:
        self.db.add(contract)
        await self.db.commit()
        await self.db.refresh(contract)
        return contract

    async def delete(self, contract: Contract) -> None:
        await self.db.delete(contract)
        await self.db.commit()
