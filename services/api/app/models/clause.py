import uuid
from sqlalchemy import String, ForeignKey, Integer, Float, Boolean, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional
from app.models.base import Base

class Clause(Base):
    __tablename__ = "clauses"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    contract_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("contracts.id", ondelete="CASCADE"), index=True)
    text: Mapped[str] = mapped_column(Text)
    position_index: Mapped[int] = mapped_column(Integer)
    
    # Analysis Fields
    risk_level: Mapped[str] = mapped_column(String(50)) # HIGH, MEDIUM, LOW, SAFE
    risk_category: Mapped[Optional[str]] = mapped_column(String(100))
    plain_english: Mapped[Optional[str]] = mapped_column(Text)
    worst_case: Mapped[Optional[str]] = mapped_column(Text)
    financial_exposure: Mapped[Optional[str]] = mapped_column(String(255))
    negotiable: Mapped[bool] = mapped_column(Boolean, default=False)
    confidence: Mapped[float] = mapped_column(Float, default=1.0)
    
    # Consequence Fields (Feature 3)
    headline: Mapped[Optional[str]] = mapped_column(String(255))
    scenario: Mapped[Optional[str]] = mapped_column(Text)
    probability: Mapped[Optional[str]] = mapped_column(String(50)) # Low, Medium, High

    # Relationships
    contract = relationship("Contract", back_populates="clauses")
    counter_offers = relationship("CounterOffer", back_populates="clause", cascade="all, delete-orphan")
    precedent_matches = relationship("PrecedentMatch", back_populates="clause", cascade="all, delete-orphan")
