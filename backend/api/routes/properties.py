"""
Property Routes — CRUD + Full Form Upsert
==========================================
Direct port of `backend/api/routes/properties.routes.ts`.
"""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, status
from sqlalchemy.orm import Session

from api.deps import CurrentUser, DbSession
from models.schemas.property import PropertyInput, PropertyResponse
from models.db import Property
from repositories.client_repo import ClientRepository
from repositories.property_repo import PropertyRepository

router = APIRouter(prefix="/api/properties", tags=["properties"])


@router.get("/")
async def list_properties(db: DbSession, _: CurrentUser):
    """List all properties."""
    props = PropertyRepository.list_all(db)
    return [PropertyResponse.model_validate(p) for p in props]


@router.get("/{property_id}")
async def get_property(property_id: str, db: DbSession, _: CurrentUser):
    """Get a single property."""
    prop = PropertyRepository.get_by_id(db, property_id)
    if not prop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "NOT_FOUND", "message": "Propriété non trouvée"},
        )
    return PropertyResponse.model_validate(prop)


@router.post("/input")
async def input_property(data: PropertyInput, db: DbSession, _: CurrentUser):
    """
    Full formulaire client — upsert (create or update) a property for a client.
    Port of the POST /api/properties/input route from the TS backend.
    """
    # Check if property already exists for this client
    existing = PropertyRepository.get_by_client_id(db, data.client_id)

    update_data = data.model_dump(exclude={"client_id"})
    # Handle booleans
    now = datetime.now(timezone.utc)

    if existing:
        # UPDATE existing property
        for key, value in update_data.items():
            if value is not None:
                setattr(existing, key, value)
        existing.form_completed = True
        existing.updated_at = now
        db.commit()
        db.refresh(existing)
        return PropertyResponse.model_validate(existing)

    # CREATE new property
    prop_data = {"client_id": data.client_id, **update_data}
    prop_data["form_completed"] = True
    prop = Property(**prop_data)
    db.add(prop)
    db.commit()
    db.refresh(prop)
    return PropertyResponse.model_validate(prop)


@router.delete("/{property_id}")
async def delete_property(property_id: str, db: DbSession, _: CurrentUser):
    """Delete a property."""
    prop = PropertyRepository.get_by_id(db, property_id)
    if not prop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "NOT_FOUND", "message": "Propriété non trouvée"},
        )
    PropertyRepository.delete(db, prop)
    return {"success": True}
