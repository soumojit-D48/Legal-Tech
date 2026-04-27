import uuid
from sqlalchemy import String, ForeignKey, Float, JSON, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, List
from app.models.base import Base

class PrecedentMatch(Base):
    __tablename__ = "precedent_matches"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    clause_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("clauses.id", ondelete="CASCADE"), index=True)
    
    precedent_summary: Mapped[Optional[str]] = mapped_column(Text)
    enforcement_likelihood: Mapped[Optional[str]] = mapped_column(String(50)) # Likely, Unlikely, etc.
    confidence_score: Mapped[float] = mapped_column(Float, default=0.0)
    cited_cases: Mapped[Optional[List[dict]]] = mapped_column(JSON) # List of {name, year, jurisdiction, outcome}

    # Relationships
    clause = relationship("Clause", back_populates="precedent_matches")
