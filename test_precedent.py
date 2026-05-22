import asyncio
import os
import sys
from uuid import UUID
from dotenv import load_dotenv

# Load env before any imports
load_dotenv()

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from services.api.app.db.session import SessionLocal
from services.api.app.models.clause import Clause
from services.api.app.models.precedent_match import PrecedentMatch
from sqlalchemy import select
from services.ai.app.pipelines.precedent_retrieval import run_precedent_retrieval_for_all_high_clauses, HighRiskClause

async def main():
    async with SessionLocal() as db:
        # Find a high risk clause
        result = await db.execute(select(Clause).where(Clause.risk_level == 'HIGH'))
        clause = result.scalars().first()
        
        if not clause:
            print("No high risk clauses found.")
            return

        print(f"Testing precedent generation for clause {clause.id}")
        high_clauses = [
            HighRiskClause(
                clause_id=str(clause.id),
                clause_type=clause.risk_category or "other",
                clause_text=clause.text,
                risk_category=clause.risk_category or "other",
            )
        ]
        
        try:
            precedent_results = run_precedent_retrieval_for_all_high_clauses(high_clauses)
            print("Successfully ran retrieval!")
            for pm in precedent_results:
                print(pm)
                
                # Check if it already exists
                existing = await db.execute(select(PrecedentMatch).where(PrecedentMatch.clause_id == UUID(pm.clause_id)))
                if not existing.scalars().first():
                    match_record = PrecedentMatch(
                        clause_id=UUID(pm.clause_id),
                        precedent_summary=pm.precedent_summary,
                        enforcement_likelihood=pm.enforcement_likelihood,
                        confidence_score=pm.confidence_score,
                        cited_cases=[c.model_dump() for c in pm.cited_cases]
                    )
                    db.add(match_record)
            await db.commit()
            print("Successfully committed to DB!")
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
