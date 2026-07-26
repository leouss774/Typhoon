"""
Assessment Routes — CRUD + Expert Forms + Evaluation
=====================================================
Combines routes from:
  - `backend/api/routes/assessments.routes.ts`
  - `backend/api/routes/expert-form.routes.ts`
  - `backend/api/routes/evaluate.routes.ts`

All mounted under `/api/assessments`.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, status
from sqlalchemy.orm import Session

from api.deps import CurrentUser, DbSession
from models.schemas.assessment import (
    AssessmentResponse,
    EvaluateRequest,
    EvaluationReportResponse,
    ExpertFormResponse,
    ExpertFormSave,
    StatusUpdate,
)
from repositories.assessment_repo import AssessmentRepository
from services.mistral_service import MistralService

router = APIRouter(prefix="/api/assessments", tags=["assessments"])


# ═══════════════════════════════════════════════════════════════
#  Basic CRUD
# ═══════════════════════════════════════════════════════════════

@router.get("/")
async def list_assessments(db: DbSession, current_user: CurrentUser):
    """List assessments for the logged-in user."""
    assessments = AssessmentRepository.list_by_user(db, current_user.sub)
    return [AssessmentResponse.model_validate(a) for a in assessments]


@router.get("/{assessment_id}")
async def get_assessment(assessment_id: str, db: DbSession, _: CurrentUser):
    """Get a single assessment."""
    assessment = AssessmentRepository.get_by_id(db, assessment_id)
    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "NOT_FOUND", "message": "Evaluation non trouvée"},
        )
    return AssessmentResponse.model_validate(assessment)


@router.patch("/{assessment_id}/status")
async def update_assessment_status(
    assessment_id: str, data: StatusUpdate, db: DbSession, _: CurrentUser
):
    """Update assessment workflow status."""
    assessment = AssessmentRepository.get_by_id(db, assessment_id)
    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "NOT_FOUND", "message": "Evaluation non trouvée"},
        )
    AssessmentRepository.update_status(db, assessment, data.status)
    return {"success": True, "status": data.status}


@router.delete("/{assessment_id}")
async def delete_assessment(assessment_id: str, db: DbSession, _: CurrentUser):
    """Delete an assessment."""
    assessment = AssessmentRepository.get_by_id(db, assessment_id)
    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "NOT_FOUND", "message": "Evaluation non trouvée"},
        )
    AssessmentRepository.delete(db, assessment)
    return {"success": True}


# ═══════════════════════════════════════════════════════════════
#  Expert Forms
# ═══════════════════════════════════════════════════════════════

@router.post("/{assessment_id}/expert-form")
async def save_expert_form(
    assessment_id: str, data: ExpertFormSave, db: DbSession, _: CurrentUser
):
    """Save / upsert expert form data for an assessment."""
    assessment = AssessmentRepository.get_by_id(db, assessment_id)
    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "NOT_FOUND", "message": "Évaluation non trouvée"},
        )

    fields_json = json.dumps(data.fields)
    recommendations_json = json.dumps(data.recommendations) if data.recommendations else None

    AssessmentRepository.upsert_expert_form(db, assessment_id, fields_json, recommendations_json)

    # Advance status to en_expertise
    assessment.status = "en_expertise"
    assessment.updated_at = datetime.now(timezone.utc)
    db.commit()

    return {"success": True}


@router.get("/{assessment_id}/expert-form")
async def get_expert_form(assessment_id: str, db: DbSession, _: CurrentUser):
    """Load expert form data for an assessment."""
    form = AssessmentRepository.get_expert_form(db, assessment_id)
    if not form:
        return ExpertFormResponse(fields=None, recommendations=None, updated_at=None)

    return ExpertFormResponse(
        fields=json.loads(form.fields),
        recommendations=json.loads(form.recommendations) if form.recommendations else [],
        updated_at=form.updated_at,
    )


# ═══════════════════════════════════════════════════════════════
#  Evaluation Reports (Scoring + Mistral)
# ═══════════════════════════════════════════════════════════════

@router.post("/{assessment_id}/evaluate")
async def evaluate_assessment(
    assessment_id: str, data: EvaluateRequest, db: DbSession, _: CurrentUser
):
    """Compute scores + generate Mistral report for an assessment."""
    assessment = AssessmentRepository.get_by_id(db, assessment_id)
    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "NOT_FOUND", "message": "Évaluation non trouvée"},
        )

    # Load expert form (optional)
    expert_form = AssessmentRepository.get_expert_form(db, assessment_id)
    expert_fields = json.loads(expert_form.fields) if expert_form else {}

    # Parse stored data
    building_data = json.loads(assessment.building_data) if assessment.building_data else None
    risks_data = json.loads(assessment.risks_data) if assessment.risks_data else None

    scores = data.scores.model_dump()

    try:
        # Generate Mistral report (or deterministic fallback)
        report = await MistralService.generate_report(
            address_label=assessment.address_label,
            building_data=building_data,
            risks_data=risks_data,
            expert_fields=expert_fields,
            scores=scores,
        )

        # Upsert evaluation report
        AssessmentRepository.upsert_evaluation_report(
            db,
            assessment_id=assessment_id,
            global_score=scores.get("global_score"),
            sub_scores_json=json.dumps(scores),
            report_content_json=json.dumps(report),
        )

        # Update assessment scores and status
        assessment.status = "evalue"
        assessment.global_score = scores.get("global_score")
        assessment.inondation_score = scores.get("inondation")
        assessment.rga_score = scores.get("rga")
        assessment.tempete_score = scores.get("tempete")
        assessment.incendie_score = scores.get("incendie")
        assessment.seisme_score = scores.get("seisme")
        assessment.updated_at = datetime.now(timezone.utc)
        db.commit()

        return {"success": True, "report": report}
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail={"error": "MISTRAL_ERROR", "message": str(err)},
        )


@router.get("/{assessment_id}/report")
async def get_report(assessment_id: str, db: DbSession, _: CurrentUser):
    """Retrieve stored evaluation report."""
    report = AssessmentRepository.get_evaluation_report(db, assessment_id)
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "NOT_FOUND", "message": "Rapport non trouvé"},
        )

    return EvaluationReportResponse(
        global_score=report.global_score,
        sub_scores=json.loads(report.sub_scores) if report.sub_scores else None,
        report=json.loads(report.report_content) if report.report_content else None,
        generated_at=report.generated_at,
    )
