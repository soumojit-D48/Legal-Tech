import uuid
from sqlalchemy import Integer, String, ForeignKey, JSON, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, List
from app.models.base import Base

class AnalysisResult(Base):
    __tablename__ = "analysis_results"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    contract_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("contracts.id", ondelete="CASCADE"), index=True)
    
    # Summary Fields
    overall_risk_score: Mapped[int] = mapped_column(Integer, default=0)
    should_sign: Mapped[Optional[str]] = mapped_column(String(50)) # Yes, No, Yes with changes
    top_concerns: Mapped[Optional[List[str]]] = mapped_column(JSON)
    top_positives: Mapped[Optional[List[str]]] = mapped_column(JSON)
    
    # Power Analysis Fields
    negotiating_power: Mapped[Optional[str]] = mapped_column(String(50)) # Strong, Moderate, Weak
    power_score: Mapped[int] = mapped_column(Integer, default=0)
    power_label: Mapped[Optional[str]] = mapped_column(String(100))
    leverage_points: Mapped[Optional[List[str]]] = mapped_column(JSON)

    # Relationships
    contract = relationship("Contract", back_populates="analysis_results")
