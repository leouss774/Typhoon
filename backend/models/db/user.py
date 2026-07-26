"""
User ORM Model
===============
Port of `backend/database/schema.ts` → `users` table.
Stores platform users (assureurs and assurés).
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base
from models.db.mixins import TimestampMixin


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column("password_hash", String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False, default="assureur")
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)

    # Relationships
    clients = relationship("Client", back_populates="user", cascade="all, delete-orphan")
    assessments = relationship("Assessment", back_populates="user")

    def __repr__(self) -> str:
        return f"<User {self.email} ({self.role})>"
