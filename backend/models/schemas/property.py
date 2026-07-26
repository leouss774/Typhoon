"""
Property Schemas
================
Port of `backend/api/routes/properties.routes.ts` property input schema.
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class PropertyInput(BaseModel):
    """Full client form (50+ fields). Matches the Zod schema in the original routes."""

    # Client link
    client_id: str = Field(..., min_length=1)

    # Address
    address: str = Field(..., min_length=1)
    postal_code: str | None = None
    city: str | None = None

    # General
    type_bien: str | None = None
    surface: float | None = Field(None, gt=0, le=10000)
    nb_pieces: int | None = Field(None, ge=1, le=50)
    nb_etages: int | None = Field(None, ge=0, le=50)
    annee_construction: int | None = Field(None, ge=1700, le=2026)
    annee_renovation: int | None = Field(None, ge=1700, le=2026)

    # Structure
    type_structure: str | None = None
    etat_structure: str | None = None
    fissures: str | None = None
    affaissement: str | None = None

    # Roof & Insulation
    type_toiture: str | None = None
    age_toiture: int | None = Field(None, ge=0, le=200)
    annee_toiture: int | None = Field(None, ge=1900, le=2026)
    etat_toiture: str | None = None
    isolation_toiture: str | None = None
    isolation_murs: str | None = None
    isolation_sol: str | None = None
    infiltrations: str | None = None

    # Basement & Equipment
    presence_sous_sol: bool | None = None
    presence_cave: bool | None = None
    presence_garage: bool | None = None
    occupation: str | None = None
    climatisation: bool | None = None
    chauffage_principal: str | None = None

    # Electricity & Safety
    installation_electrique_annee: int | None = Field(None, ge=1900, le=2026)
    presence_detecteurs_fumee: bool | None = None

    # Exposure & Environment
    exposition_solaire: str | None = None
    zone_mitoyennete: str | None = None

    # Flood
    hauteur_plancher: float | None = Field(None, ge=0, le=500)
    clapet_anti_retour: bool | None = None
    equipements_elec_sous_sol: bool | None = None

    # RGA
    profondeur_fondations: str | None = None
    arbres_proches: bool | None = None
    materiau_toit: str | None = None
    panneaux_solaires: bool | None = None

    # Insurance
    capital_assure: float | None = None

    # DPE & BDNB
    dpe_class: str | None = None
    ban_id: str | None = None
    longitude: float | None = None
    latitude: float | None = None

    # Observations
    observations: str | None = None


class PropertyResponse(BaseModel):
    id: str
    client_id: str
    address: str
    postal_code: str | None
    city: str | None
    type_bien: str | None
    surface: float | None
    dpe_class: str | None
    built_year: int | None
    ban_id: str | None
    longitude: float | None
    latitude: float | None
    form_completed: bool | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
