import asyncio
from sqlalchemy import text
from app.db.session import async_session
async def main():
 db = async_session()
 async with db.begin():
  res = await db.execute(text("SELECT id, contract_id FROM clauses"))
  for row in res:
   print(f'Clause: {row[0]}, Contract: {row[1]}')
 await db.close()
asyncio.run(main())
