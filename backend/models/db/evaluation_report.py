"""
EvaluationReport ORM Model
==========================
Port of `backend/database/schema.ts` → `evaluation_reports` table.
Stores computed scores and Mistral-generated report content.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base


class EvaluationReport(Base):
    __tablename__ = "evaluation_reports"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    assessment_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("assessments.id", ondelete="cascade"), nullable=False
    )

    # Computed scores
    global_score: Mapped[int | None] = mapped_column("global_score", Integer, nullable=True)
    sub_scores: Mapped[str | None] = mapped_column("sub_scores", Text, nullable=True)  # JSON

    # Mistral-generated report
    report_content: Mapped[str | None] = mapped_column("report_content", Text, nullable=True)  # JSON

    generated_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    # Relationships
    assessment = relationship("Assessment", back_populates="evaluation_report")

    def __repr__(self) -> str:
        return f"<EvaluationReport for assessment {self.assessment_id[:8]}>"
