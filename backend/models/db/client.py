"""
Client ORM Model
================
Port of `backend/database/schema.ts` → `clients` table.
Each client belongs to one user (assureur).
"""

from __future__ import annotations

import uuid

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base
from models.db.mixins import TimestampMixin as _TimestampMixin


class Client(Base, _TimestampMixin):
    __tablename__ = "clients"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="cascade"), nullable=False
    )
    civility: Mapped[str | None] = mapped_column(String(10), nullable=True)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    insured_address: Mapped[str | None] = mapped_column("insured_address", String(255), nullable=True)
    insured_postal_code: Mapped[str | None] = mapped_column("insured_postal_code", String(10), nullable=True)
    insured_city: Mapped[str | None] = mapped_column("insured_city", String(100), nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active")

    # Relationships
    user = relationship("User", back_populates="clients")
    properties = relationship("Property", back_populates="client", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="client", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Client {self.first_name} {self.last_name}>"
