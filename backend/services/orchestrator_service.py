"""
Risk Assessment Orchestrator Service
=====================================
Direct port of `backend/services/orchestrator.service.ts`.

Calls ALL providers in parallel and assembles a RiskAssessmentInput + scores.
Uses real API calls for all providers — no hardcoded fallbacks (except when
an API actually fails / is unreachable).

Providers:
  ├─ Géorisques v1/v2      (risks + enrichment)
  ├─ IGN altitude           (geography)
  ├─ WFS BD TOPO            (distance to waterway)
  ├─ WFS Masque Forêt       (distance to forest)
  ├─ Open-Meteo climate     (climate + projections)
  ├─ BDNB building          (property data — if banId available)
  ├─ GASPAR CATNAT          (catastrophes naturelles history)
  ├─ DVF lookup             (valuation — by department, local JSON)
  └─ DRIAS lookup           (climate — by department, local JSON)
"""

from __future__ import annotations

import asyncio
import uuid
from datetime import datetime, timezone
from typing import Any

import httpx

from services.bdnb_service import BdnbService
from services.cache_service import AssessmentCache
from services.georisques_service import GeorisquesService
from services.ign_service import IgnService
from services.lookup_service import LookupService
from services.scoring_service import ScoringEngine
from services.wfs_service import WfsService


async def _fetch_catnat_count(commune_code: str) -> int:
    """Fetch number of CATNAT events in the last 10 years."""
    try:
        async with httpx.AsyncClient(timeout=6.0) as client:
            res = await client.get(
                f"https://www.georisques.gouv.fr/api/v1/gaspar/catnat?code_insee={commune_code}",
                headers={"Accept": "application/json"},
            )
            if not res.is_success:
                return 0
            raw = res.json()
            records = raw.get("data", raw if isinstance(raw, list) else [])
            if not isinstance(records, list):
                return 0
            cutoff = datetime.now(timezone.utc)
            cutoff = cutoff.replace(year=cutoff.year - 10)
            count = 0
            for r in records:
                date_str = r.get("date_publication_arrete") or r.get("date_arrete") or r.get("date_debut")
                if date_str:
                    try:
                        d = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                        if d >= cutoff:
                            count += 1
                    except (ValueError, TypeError):
                        pass
            return count
    except Exception:
        return 0


# ─── Empty factories ─────────────────────────────────────────────

def _empty_building(dept_code: str) -> dict[str, Any]:
    return {
        "built_year": None,
        "construction_period": None,
        "surface_utile": None,
        "surface_emprise": None,
        "levels": None,
        "height": None,
        "dpe_class": None,
        "energy_consumption": None,
        "emission_ges": None,
        "wall_material": None,
        "roof_material": None,
        "heating_type": None,
        "usage_type": None,
        "nb_logements": None,
        "department_code": dept_code,
        "nb_logements_rnc": None,
        "clay_exposure": None,
        "altitude_sol_mean": None,
        "heating_energy_type": None,
        "parcel_ids": None,
        "quartier_prioritaire": None,
        "zone_patrimoniale": None,
    }


def _empty_natural_risks() -> dict[str, Any]:
    empty = {"present": False, "level": None}
    return {
        "inondation": dict(empty),
        "remontee_nappe": dict(empty),
        "risque_cotier": dict(empty),
        "seisme": dict(empty),
        "mouvement_terrain": dict(empty),
        "retrait_gonflement_argile": dict(empty),
        "recul_trait_cote": dict(empty),
        "avalanche": dict(empty),
        "feu_foret": dict(empty),
        "eruption_volcanique": dict(empty),
        "cyclone": dict(empty),
        "radon": dict(empty),
    }


def _empty_techno_risks() -> dict[str, Any]:
    empty = {"present": False, "level": None}
    return {
        "icpe": dict(empty),
        "nucleaire": dict(empty),
        "canalisations_matieres_dangereuses": dict(empty),
        "pollution_sols": dict(empty),
        "rupture_barrage": dict(empty),
        "risque_minier": dict(empty),
    }


class OrchestratorService:
    """
    Master risk assessment orchestrator.
    Calls all providers → assembles input → scores → caches → returns.
    """

    @staticmethod
    async def run_assessment(
        latitude: float,
        longitude: float,
        address: str,
        ban_id: str | None = None,
        commune_code: str | None = None,
        commune_name: str | None = None,
        department_code: str | None = None,
        property_id: str | None = None,
    ) -> dict[str, Any]:
        """
        Run a full risk assessment.

        Returns:
            dict with keys:
                - property (BuildingData)
                - valuation (DvfData | None)
                - geography (IgnData)
                - risks (RiskData)
                - climate (ClimateData)
                - metadata (AssessmentMetadata)
                - scores (PerilScores)
                - assessment_id (str)
        """
        lat, lon = latitude, longitude

        # Check 24h cache first
        cached = AssessmentCache.get(lat, lon)
        if cached:
            return cached

        dept_code = department_code or (ban_id[:2] if ban_id else "75")
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

        # Launch ALL providers in parallel
        georisques_task = GeorisquesService.fetch_georisques_data(lon, lat)
        ign_alt_task = IgnService.fetch_altitude(lon, lat)
        climate_task = IgnService.fetch_climate(lon, lat)

        building_task = (
            BdnbService.fetch_building_by_ban_id(ban_id)
            if ban_id
            else asyncio.ensure_future(asyncio.sleep(0, _empty_building(dept_code)))
        )

        catnat_task = (
            _fetch_catnat_count(commune_code)
            if commune_code
            else asyncio.ensure_future(asyncio.sleep(0, 0))
        )

        water_dist_task = WfsService.fetch_waterway_distance(lon, lat)
        forest_dist_task = WfsService.fetch_forest_distance(lon, lat)

        results = await asyncio.gather(
            georisques_task,
            ign_alt_task,
            climate_task,
            building_task,
            catnat_task,
            water_dist_task,
            forest_dist_task,
            return_exceptions=True,
        )

        # ── Extract results with fallbacks ──
        georisques_data: Any = None
        ign_alt: dict[str, Any] = {"altitude": None, "slope": None}
        climate: dict[str, Any] | None = None
        building: dict[str, Any] = _empty_building(dept_code)
        catnat_count: int = 0
        water_dist: float | None = None
        forest_dist: float | None = None

        for i, r in enumerate(results):
            if isinstance(r, Exception):
                continue
            if i == 0:
                georisques_data = r
            elif i == 1:
                ign_alt = r
            elif i == 2:
                climate = r
            elif i == 3:
                building = r
            elif i == 4:
                catnat_count = r
            elif i == 5:
                water_dist = r
            elif i == 6:
                forest_dist = r

        # ── Geography ──
        geography = {
            "parcel_id": None,
            "altitude": ign_alt.get("altitude"),
            "slope": ign_alt.get("slope"),
            "distance_to_waterway": water_dist,
            "distance_to_forest": forest_dist,
            "distance_fire_station": None,
            "land_use": "urban",
        }

        # ── Valuation — DVF lookup ──
        dvf_lookup = LookupService.lookup_dvf(dept_code)
        valuation = None
        if dvf_lookup:
            valuation = {
                "reconstruction_value_per_sqm": dvf_lookup.reconstruction_value_per_sqm,
                "last_transaction_price_per_sqm": dvf_lookup.last_transaction_price_per_sqm,
                "last_transaction_date": None,
                "last_transaction_type": None,
            }

        # ── DRIAS lookup ──
        drias_lookup = LookupService.lookup_drias(dept_code)
        drias_data = None
        if drias_lookup:
            d = drias_lookup.drias
            drias_data = {
                "method": drias_lookup.method,
                "warming_level": drias_lookup.warming_level,
                "heatwave_days": d.heatwave_days,
                "tropical_nights": d.tropical_nights,
                "summer_days": d.summer_days,
                "heavy_precip_days": d.heavy_precip_days,
                "max5day_precip": d.max5day_precip,
                "consecutive_dry_days": d.consecutive_dry_days,
                "fire_weather_index": d.fire_weather_index,
                "frost_days": d.frost_days,
                "data_source": d.data_source,
            }

        # ── Combine risks data ──
        if georisques_data:
            risks_data = {
                "naturels": georisques_data.risks.get("naturels", _empty_natural_risks()),
                "technologiques": georisques_data.risks.get("technologiques", _empty_techno_risks()),
                "commune": georisques_data.commune or commune_name,
                "commune_code": georisques_data.commune_code or commune_code,
                "natural_risk_count": georisques_data.risks.get("natural_risk_count", 0),
                "techno_risk_count": georisques_data.risks.get("techno_risk_count", 0),
                "catnat_last_10_years": catnat_count,
                "ppr_approved": True,
                "enrichment": (
                    {"argile_exposition": georisques_data.enrichment.get("argile_exposition"),
                     "cavities_nearby": georisques_data.enrichment.get("cavities_nearby"),
                     "polluted_sites_nearby": georisques_data.enrichment.get("polluted_sites_nearby")}
                    if georisques_data.enrichment else None
                ),
            }
        else:
            risks_data = {
                "naturels": _empty_natural_risks(),
                "technologiques": _empty_techno_risks(),
                "commune": commune_name,
                "commune_code": commune_code,
                "natural_risk_count": 0,
                "techno_risk_count": 0,
                "catnat_last_10_years": catnat_count,
                "ppr_approved": True,
                "enrichment": None,
            }

        # ── Combine climate data ──
        if climate is None:
            climate = {
                "freeze_days_per_year": None,
                "storm_frequency": None,
                "hail_risk": None,
                "annual_precipitation": None,
                "heatwave_days_per_year": None,
                "wind_zone": None,
                "snow_zone": None,
                "projected_freeze_days": None,
                "projected_heatwave_days": None,
                "projected_precipitation": None,
                "projected_storm_frequency": None,
                "projection_model": None,
                "projection_scenario": None,
                "mean_humidity": None,
                "max_humidity": None,
                "min_humidity": None,
                "soil_moisture": None,
                "projected_soil_moisture": None,
            }
        climate["drias"] = drias_data

        # ── Build metadata ──
        metadata = {
            "address_label": address,
            "longitude": lon,
            "latitude": lat,
            "commune_name": georisques_data.commune if georisques_data and georisques_data.commune else (commune_name or ""),
            "commune_code": georisques_data.commune_code if georisques_data and georisques_data.commune_code else (commune_code or ""),
            "assessment_date": today,
            "data_freshness": {
                "bdnb": today if building.get("built_year") else None,
                "georisques": today if georisques_data else None,
                "dvf": today if dvf_lookup else None,
                "ign": today if ign_alt.get("altitude") is not None else None,
                "openmeteo_climate": today if climate.get("freeze_days_per_year") is not None else None,
                "drias": today if drias_data else None,
            },
        }

        # ── Build full assessment input for scoring ──
        full_input = {
            "property": building,
            "valuation": valuation,
            "geography": geography,
            "risks": risks_data,
            "climate": climate,
            "metadata": metadata,
        }

        # ── Compute scores ──
        scores = ScoringEngine.score_all(full_input)

        assessment_id = str(uuid.uuid4())

        result = {
            "assessment_id": assessment_id,
            "property": building,
            "valuation": valuation,
            "geography": geography,
            "risks": risks_data,
            "climate": climate,
            "metadata": metadata,
            "scores": scores,
        }

        # Write to cache
        AssessmentCache.set(lat, lon, result)

        return result
