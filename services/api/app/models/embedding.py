import uuid
from sqlalchemy import ForeignKey, Integer, String, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pgvector.sqlalchemy import Vector
from typing import Optional, List
from app.models.base import Base

class Embedding(Base):
    __tablename__ = "embeddings"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    contract_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("contracts.id", ondelete="CASCADE"), index=True)
    
    chunk_text: Mapped[str] = mapped_column(Text)
    chunk_index: Mapped[int] = mapped_column(Integer)
    embedding: Mapped[List[float]] = mapped_column(Vector(384)) # Using 384 for all-MiniLM-L6-v2
    embedding_type: Mapped[str] = mapped_column(String(50)) # contract_qa, favorable_clause, precedent
    
    # Metadata for non-contract embeddings (precedent, favorable)
    metadata_json: Mapped[Optional[dict]] = mapped_column(JSON)

    # Relationships
    contract = relationship("Contract", back_populates="embeddings")
