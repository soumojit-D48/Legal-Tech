import asyncio
from sqlalchemy import text
from app.db.session import async_session
async def main():
 db = async_session()
 async with db.begin():
  res = await db.execute(text("SELECT contract_id FROM clauses WHERE id = '6688c193-2647-4591-88dc-b99a066110d7'"))
  print(res.scalar())
 await db.close()
asyncio.run(main())
