"""
ExpertForm ORM Model
====================
Port of `backend/database/schema.ts` → `expert_forms` table.
Stores expert-filled form fields and recommendations for an assessment.
"""

from __future__ import annotations

import uuid

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base
from models.db.mixins import TimestampMixin


class ExpertForm(Base, TimestampMixin):
    __tablename__ = "expert_forms"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    assessment_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("assessments.id", ondelete="cascade"), nullable=False
    )

    # All form fields as JSON string
    fields: Mapped[str] = mapped_column(Text, nullable=False)
    # Recommendations as JSON string (list of strings)
    recommendations: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    assessment = relationship("Assessment", back_populates="expert_form")

    def __repr__(self) -> str:
        return f"<ExpertForm for assessment {self.assessment_id[:8]}>"
