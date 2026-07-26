"""
Assessment Schemas
==================
Port of `backend/models/types.ts` Assessment section and evaluation routes.
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class StatusUpdate(BaseModel):
    status: str = Field(..., pattern=r"^(nouveau|en_localisation|en_expertise|en_inspection|evalue)$")


class ExpertFormSave(BaseModel):
    fields: dict[str, str]
    recommendations: list[str] | None = None


class ExpertFormResponse(BaseModel):
    fields: dict[str, str] | None = None
    recommendations: list[str] | None = None
    updated_at: datetime | None = None


class EvaluateScores(BaseModel):
    global_score: int = Field(..., ge=0, le=100)
    inondation: int = Field(..., ge=0, le=100)
    rga: int = Field(..., ge=0, le=100)
    tempete: int = Field(..., ge=0, le=100)
    incendie: int = Field(..., ge=0, le=100)
    seisme: int = Field(..., ge=0, le=100)


class EvaluateRequest(BaseModel):
    scores: EvaluateScores


class AssessmentResponse(BaseModel):
    id: str
    property_id: str | None
    user_id: str | None
    address_label: str
    longitude: float
    latitude: float
    status: str
    global_score: int | None
    inondation_score: int | None
    rga_score: int | None
    tempete_score: int | None
    incendie_score: int | None
    seisme_score: int | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class EvaluationReportResponse(BaseModel):
    global_score: int | None
    sub_scores: dict | None
    report: dict | None
    generated_at: datetime | None
