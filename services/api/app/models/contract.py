import uuid
from datetime import datetime, timezone
from sqlalchemy import String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, List
from app.models.base import Base

class Contract(Base):
    __tablename__ = "contracts"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    file_ref: Mapped[str] = mapped_column(String(511))  # Uploadthing URL
    contract_type: Mapped[Optional[str]] = mapped_column(String(100))
    detected_language: Mapped[str] = mapped_column(String(10), default="en")
    party_roles: Mapped[Optional[dict]] = mapped_column(JSON) # e.g. {"roles": ["employer", "employee"]}
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, 
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    user = relationship("User", back_populates="contracts")
    clauses = relationship("Clause", back_populates="contract", cascade="all, delete-orphan")
    scan_jobs = relationship("ScanJob", back_populates="contract", cascade="all, delete-orphan")
    analysis_results = relationship("AnalysisResult", back_populates="contract", cascade="all, delete-orphan")
    embeddings = relationship("Embedding", back_populates="contract", cascade="all, delete-orphan")
    reports = relationship("Report", back_populates="contract", cascade="all, delete-orphan")
