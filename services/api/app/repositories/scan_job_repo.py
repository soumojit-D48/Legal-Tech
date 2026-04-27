import uuid
from typing import Optional
from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.scan_job import ScanJob

class ScanJobRepo:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, job_id: uuid.UUID) -> Optional[ScanJob]:
        result = await self.db.execute(select(ScanJob).where(ScanJob.id == job_id))
        return result.scalar_one_or_none()

    async def get_latest_by_contract(self, contract_id: uuid.UUID) -> Optional[ScanJob]:
        result = await self.db.execute(
            select(ScanJob)
            .where(ScanJob.contract_id == contract_id)
            .order_by(ScanJob.created_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def create(self, contract_id: uuid.UUID) -> ScanJob:
        job = ScanJob(contract_id=contract_id)
        self.db.add(job)
        await self.db.commit()
        await self.db.refresh(job)
        return job

    async def update_status(self, job_id: uuid.UUID, status: str, progress: int = None, error: str = None) -> Optional[ScanJob]:
        job = await self.get_by_id(job_id)
        if not job:
            return None
        
        job.status = status
        if progress is not None:
            job.progress_pct = progress
        if error:
            job.error_message = error
        
        if status in ["complete", "failed"]:
            job.completed_at = datetime.now(timezone.utc)
            
        await self.db.commit()
        await self.db.refresh(job)
        return job
