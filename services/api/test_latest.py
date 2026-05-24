import asyncio
from uuid import UUID
from app.db.session import AsyncSessionLocal
from app.repositories import contract_repo

async def run():
    async with AsyncSessionLocal() as db:
        user_id = UUID('67a8111e-c620-4166-bd6b-6250f4ec9465')
        contracts = await contract_repo.get_all_contracts_by_user_id(db, user_id)
        for c in contracts[:2]:
            latest_job_id = str(c.scan_jobs[0].id) if getattr(c, 'scan_jobs', None) and len(c.scan_jobs) > 0 else None
            print(c.original_filename, latest_job_id)

asyncio.run(run())
