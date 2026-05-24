import asyncio
from sqlalchemy import select
from app.db.session import async_session
from app.models.clause import Clause
from app.models.contract import Contract
from uuid import UUID
async def main():
 db = async_session()
 async with db.begin():
  clause_uuid = UUID('6688c193-2647-4591-88dc-b99a066110d7')
  user_id = UUID('67a8111e-c620-4166-bd6b-6250f4ec9465')
  c = await db.execute(select(Clause).where(Clause.id == clause_uuid))
  print('Clause alone:', c.scalar())
  con = await db.execute(select(Contract).where(Contract.user_id == user_id))
  print('Contracts for user:', [str(r.id) for r in con.scalars().all()])
 await db.close()
asyncio.run(main())
