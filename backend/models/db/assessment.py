"""
Assessment ORM Model
====================
Port of `backend/database/schema.ts` → `assessments` table.
Stores risk assessment snapshots and computed scores.
"""

from __future__ import annotations

import uuid

from sqlalchemy import Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base
from models.db.mixins import TimestampMixin


class Assessment(Base, TimestampMixin):
    __tablename__ = "assessments"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    property_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("properties.id"), nullable=True
    )
    user_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=True
    )

    # ── Address snapshot ──
    address_label: Mapped[str] = mapped_column("address_label", String(255), nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)

    # ── Workflow status ──
    status: Mapped[str] = mapped_column(
        String(30), nullable=False, default="nouveau"
    )

    # ── Raw API snapshots (JSON strings) ──
    building_data: Mapped[str | None] = mapped_column("building_data", Text, nullable=True)
    geography_data: Mapped[str | None] = mapped_column("geography_data", Text, nullable=True)
    risks_data: Mapped[str | None] = mapped_column("risks_data", Text, nullable=True)
    climate_data: Mapped[str | None] = mapped_column("climate_data", Text, nullable=True)
    valuation_data: Mapped[str | None] = mapped_column("valuation_data", Text, nullable=True)
    metadata_data: Mapped[str | None] = mapped_column("metadata_data", Text, nullable=True)

    # ── Computed scores ──
    inondation_score: Mapped[int | None] = mapped_column("inondation_score", Integer, nullable=True)
    rga_score: Mapped[int | None] = mapped_column("rga_score", Integer, nullable=True)
    tempete_score: Mapped[int | None] = mapped_column("tempete_score", Integer, nullable=True)
    incendie_score: Mapped[int | None] = mapped_column("incendie_score", Integer, nullable=True)
    seisme_score: Mapped[int | None] = mapped_column("seisme_score", Integer, nullable=True)
    global_score: Mapped[int | None] = mapped_column("global_score", Integer, nullable=True)

    # Relationships
    property = relationship("Property", back_populates="assessments")
    user = relationship("User", back_populates="assessments")
    expert_form = relationship("ExpertForm", back_populates="assessment", uselist=False, cascade="all, delete-orphan")
    evaluation_report = relationship("EvaluationReport", back_populates="assessment", uselist=False, cascade="all, delete-orphan")


    def __repr__(self) -> str:
        return f"<Assessment {self.id[:8]} @ {self.address_label}>"
