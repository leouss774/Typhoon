"""
Risk Assessment Routes
======================
Port of `backend/api/routes/risk.routes.ts`.

POST /api/risk/assess — Run a full risk assessment (orchestrates all providers).
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from api.deps import DbSession, OptionalUser
from models.schemas.risk import AssessRequest, AssessResponse
from models.db import Assessment
from repositories.assessment_repo import AssessmentRepository
from services.orchestrator_service import OrchestratorService

router = APIRouter(prefix="/api/risk", tags=["risk"])


@router.post("/assess")
async def assess_risk(
    data: AssessRequest,
    db: DbSession,
    current_user: OptionalUser,
):
    """
    Run a full risk assessment for a property location.
    Orchestrates all external providers (Géorisques, BDNB, IGN, WFS, Open-Meteo, DVF, DRIAS)
    and computes scores.

    Equivalent to the original POST /api/risk/assess endpoint.
    """
    try:
        result = await OrchestratorService.run_assessment(
            latitude=data.latitude,
            longitude=data.longitude,
            address=data.address,
            ban_id=data.ban_id,
            commune_code=data.commune_code,
            commune_name=data.commune_name,
            department_code=data.department_code,
            property_id=data.property_id,
        )
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail={"error": "ASSESSMENT_FAILED", "message": str(err)},
        )

    # ── Persist assessment snapshot asynchronously ──
    try:
        assessment_data = {
            "id": result["assessment_id"],
            "property_id": data.property_id,
            "user_id": current_user.sub if current_user else None,
            "address_label": data.address,
            "longitude": data.longitude,
            "latitude": data.latitude,
            "building_data": json_dumps(result.get("property")),
            "geography_data": json_dumps(result.get("geography")),
            "risks_data": json_dumps(result.get("risks")),
            "climate_data": json_dumps(result.get("climate")),
            "valuation_data": json_dumps(result.get("valuation")),
            "metadata_data": json_dumps(result.get("metadata")),
            "inondation_score": result["scores"].get("inondation"),
            "rga_score": result["scores"].get("rga"),
            "tempete_score": result["scores"].get("tempete"),
            "incendie_score": result["scores"].get("incendie"),
            "seisme_score": result["scores"].get("seisme"),
            "global_score": result["scores"].get("global_score"),
        }
        assessment = Assessment(**assessment_data)
        db.add(assessment)
        db.commit()
    except Exception as persist_err:
        # Non-blocking — log but don't fail the response
        import logging
        logging.warning("Failed to persist assessment: %s", persist_err)
        db.rollback()

    return AssessResponse(**result)


def json_dumps(obj):
    """Safely serialize to JSON string, handling None."""
    import json
    if obj is None:
        return None
    return json.dumps(obj, ensure_ascii=False, default=str)
