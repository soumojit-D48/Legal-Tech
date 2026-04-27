import uuid
from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.report import Report

class ReportRepo:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, report_id: uuid.UUID) -> Optional[Report]:
        result = await self.db.execute(select(Report).where(Report.id == report_id))
        return result.scalar_one_or_none()

    async def get_by_share_uuid(self, share_uuid: uuid.UUID) -> Optional[Report]:
        result = await self.db.execute(select(Report).where(Report.share_uuid == share_uuid))
        return result.scalar_one_or_none()

    async def get_by_contract(self, contract_id: uuid.UUID) -> List[Report]:
        result = await self.db.execute(
            select(Report).where(Report.contract_id == contract_id).order_by(Report.created_at.desc())
        )
        return list(result.scalars().all())

    async def create(self, **kwargs) -> Report:
        report = Report(**kwargs)
        self.db.add(report)
        await self.db.commit()
        await self.db.refresh(report)
        return report

    async def delete_expired(self) -> int:
        now = datetime.now(timezone.utc)
        result = await self.db.execute(
            delete(Report).where(Report.expires_at < now)
        )
        await self.db.commit()
        return result.rowcount
