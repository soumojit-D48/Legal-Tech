import uuid
from sqlalchemy import ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional
from app.models.base import Base

class CounterOffer(Base):
    __tablename__ = "counter_offers"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    clause_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("clauses.id", ondelete="CASCADE"), index=True)
    
    aggressive_clause: Mapped[Optional[str]] = mapped_column(Text)
    balanced_clause: Mapped[Optional[str]] = mapped_column(Text)
    conservative_clause: Mapped[Optional[str]] = mapped_column(Text)
    negotiation_email: Mapped[Optional[str]] = mapped_column(Text)

    # Relationships
    clause = relationship("Clause", back_populates="counter_offers")
