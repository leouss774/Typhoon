"""
Document ORM Model
==================
Port of `backend/database/schema.ts` → `documents` table.
Stores uploaded document metadata.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    client_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("clients.id", ondelete="cascade"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    type: Mapped[str] = mapped_column(String(30), nullable=False)  # contrat, cni, rib, etc.
    url: Mapped[str] = mapped_column(String(512), nullable=False)
    size_bytes: Mapped[int | None] = mapped_column("size_bytes", Integer, nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    # Relationships
    client = relationship("Client", back_populates="documents")

    def __repr__(self) -> str:
        return f"<Document {self.name} ({self.type})>"
