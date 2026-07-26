"""
Risk Assessment Schemas
=======================
Port of `backend/models/schema.ts` and `backend/models/types.ts` risk section.
These define the full risk assessment input/output contracts.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


# ─── Request ──────────────────────────────────────────────────────

class AssessRequest(BaseModel):
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    address: str = Field(..., min_length=1)
    ban_id: str | None = None
    commune_code: str | None = None
    commune_name: str | None = None
    department_code: str | None = None
    property_id: str | None = None


# ─── Data snapshots (from providers) ─────────────────────────────

class BuildingData(BaseModel):
    built_year: int | None = None
    construction_period: str | None = None
    surface_utile: float | None = None
    surface_emprise: float | None = None
    levels: int | None = None
    height: float | None = None
    dpe_class: str | None = None
    energy_consumption: float | None = None
    emission_ges: float | None = None
    wall_material: str | None = None
    roof_material: str | None = None
    heating_type: str | None = None
    usage_type: str | None = None
    nb_logements: int | None = None
    department_code: str | None = None
    nb_logements_rnc: int | None = None
    clay_exposure: str | None = None
    altitude_sol_mean: float | None = None
    heating_energy_type: str | None = None
    parcel_ids: list[str] | None = None
    quartier_prioritaire: bool | None = None
    zone_patrimoniale: str | bool | None = None
    footprint: dict | None = None


class DvfData(BaseModel):
    reconstruction_value_per_sqm: float | None = None
    last_transaction_price_per_sqm: float | None = None
    last_transaction_date: str | None = None
    last_transaction_type: str | None = None


class IgnData(BaseModel):
    parcel_id: str | None = None
    altitude: float | None = None
    slope: str | None = None
    distance_to_waterway: float | None = None
    distance_to_forest: float | None = None
    distance_fire_station: float | None = None
    land_use: str | None = None


class RiskLevel(BaseModel):
    present: bool = False
    level: str | None = None


class NaturalRisks(BaseModel):
    inondation: RiskLevel = RiskLevel()
    remontee_nappe: RiskLevel = RiskLevel()
    risque_cotier: RiskLevel = RiskLevel()
    seisme: RiskLevel = RiskLevel()
    mouvement_terrain: RiskLevel = RiskLevel()
    retrait_gonflement_argile: RiskLevel = RiskLevel()
    recul_trait_cote: RiskLevel = RiskLevel()
    avalanche: RiskLevel = RiskLevel()
    feu_foret: RiskLevel = RiskLevel()
    eruption_volcanique: RiskLevel = RiskLevel()
    cyclone: RiskLevel = RiskLevel()
    radon: RiskLevel = RiskLevel()


class TechnoRisks(BaseModel):
    icpe: RiskLevel = RiskLevel()
    nucleaire: RiskLevel = RiskLevel()
    canalisations_matieres_dangereuses: RiskLevel = RiskLevel()
    pollution_sols: RiskLevel = RiskLevel()
    rupture_barrage: RiskLevel = RiskLevel()
    risque_minier: RiskLevel = RiskLevel()


class RiskEnrichment(BaseModel):
    argile_exposition: list[dict] | None = None
    cavities_nearby: int | None = None
    polluted_sites_nearby: int | None = None


class RiskData(BaseModel):
    naturels: NaturalRisks = NaturalRisks()
    technologiques: TechnoRisks = TechnoRisks()
    commune: str | None = None
    commune_code: str | None = None
    natural_risk_count: int = 0
    techno_risk_count: int = 0
    catnat_last_10_years: int | None = None
    ppr_approved: bool = True
    enrichment: RiskEnrichment | None = None


class DriasData(BaseModel):
    method: str = ""
    warming_level: str = ""
    heatwave_days: int | None = None
    tropical_nights: int | None = None
    summer_days: int | None = None
    heavy_precip_days: int | None = None
    max5day_precip: float | None = None
    consecutive_dry_days: int | None = None
    fire_weather_index: float | None = None
    frost_days: int | None = None
    data_source: str | None = None


class ClimateData(BaseModel):
    freeze_days_per_year: int | None = None
    storm_frequency: int | None = None
    hail_risk: int | None = None
    annual_precipitation: float | None = None
    heatwave_days_per_year: int | None = None
    wind_zone: int | None = None
    snow_zone: str | None = None
    projected_freeze_days: int | None = None
    projected_heatwave_days: int | None = None
    projected_precipitation: float | None = None
    projected_storm_frequency: int | None = None
    projection_model: str | None = None
    projection_scenario: str | None = None
    mean_humidity: float | None = None
    max_humidity: float | None = None
    min_humidity: float | None = None
    soil_moisture: float | None = None
    projected_soil_moisture: float | None = None
    drias: DriasData | None = None


class AssessmentMetadata(BaseModel):
    address_label: str = ""
    longitude: float = 0.0
    latitude: float = 0.0
    commune_name: str = ""
    commune_code: str = ""
    assessment_date: str = ""
    data_freshness: dict[str, str | None] = {}


class PerilScores(BaseModel):
    inondation: int = 0
    rga: int = 0
    tempete: int = 0
    incendie: int = 0
    seisme: int = 0
    global_score: int = 0


class AssessResponse(BaseModel):
    assessment_id: str
    property: BuildingData
    valuation: DvfData | None = None
    geography: IgnData
    risks: RiskData
    climate: ClimateData
    metadata: AssessmentMetadata
    scores: PerilScores
