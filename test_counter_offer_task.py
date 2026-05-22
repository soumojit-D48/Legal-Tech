import sys
import asyncio
from uuid import UUID

# add to path
sys.path.insert(0, r"c:\Users\subhankar nath\Desktop\Legal-Tech")

from services.api.app.db.session import SessionLocal
from services.api.app.models.clause import Clause
from sqlalchemy import select

async def main():
    async with SessionLocal() as db:
        clause_result = await db.execute(select(Clause).limit(1))
        clause = clause_result.scalars().first()
        
    if not clause:
        print("No clause found")
        return
        
    print(f"Testing with clause_id={clause.id}")
    return str(clause.id)

if __name__ == "__main__":
    clause_id = asyncio.run(main())
    if clause_id:
        from apps.worker.tasks.generate_counter_offer import generate_counter_offer_task
        try:
            res = generate_counter_offer_task.apply(args=[clause_id])
            print("Success!", res.result)
        except Exception as e:
            import traceback
            traceback.print_exc()
