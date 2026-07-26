"""
Géorisques Service — Server-side fetcher
=========================================
Direct port of `backend/services/georisques.service.ts`.

Fetches natural and technological risk data from georisques.gouv.fr.
Uses v2 API if a token is configured, falls back to v1 public API.
"""

from __future__ import annotations

from typing import Any

import httpx

from core.config import settings

CLIENT_TIMEOUT = 10.0  # seconds


class GeorisquesResult:
    def __init__(
        self,
        risks: dict[str, Any],
        commune: str | None,
        commune_code: str | None,
        enrichment: dict[str, Any] | None,
        source: str,
    ):
        self.risks = risks
        self.commune = commune
        self.commune_code = commune_code
        self.enrichment = enrichment
        self.source = source


def _empty_level() -> dict[str, Any]:
    return {"present": False, "level": None}


def _empty_natural_risks() -> dict[str, Any]:
    return {
        "inondation": _empty_level(),
        "remontee_nappe": _empty_level(),
        "risque_cotier": _empty_level(),
        "seisme": _empty_level(),
        "mouvement_terrain": _empty_level(),
        "retrait_gonflement_argile": _empty_level(),
        "recul_trait_cote": _empty_level(),
        "avalanche": _empty_level(),
        "feu_foret": _empty_level(),
        "eruption_volcanique": _empty_level(),
        "cyclone": _empty_level(),
        "radon": _empty_level(),
    }


def _empty_techno_risks() -> dict[str, Any]:
    return {
        "icpe": _empty_level(),
        "nucleaire": _empty_level(),
        "canalisations_matieres_dangereuses": _empty_level(),
        "pollution_sols": _empty_level(),
        "rupture_barrage": _empty_level(),
        "risque_minier": _empty_level(),
    }


class GeorisquesService:
    """Fetch risk data from Géorisques API (v2 with token, v1 fallback)."""

    @staticmethod
    async def fetch_georisques_data(lon: float, lat: float) -> GeorisquesResult:
        token = settings.GEORISQUES_V2_TOKEN

        # Try v2 API if token is configured
        if token:
            try:
                async with httpx.AsyncClient(timeout=CLIENT_TIMEOUT) as client:
                    headers = {
                        "Authorization": f"Bearer {token}",
                        "Accept": "application/json",
                    }
                    res = await client.get(
                        f"https://georisques.gouv.fr/api/v2/rga?latlon={lat},{lon}",
                        headers=headers,
                    )
                    if res.is_success:
                        data = res.json()
                        naturels = _empty_natural_risks()
                        alea = data.get("alea")
                        if alea:
                            code = str(alea).lower()
                            level = "fort" if "fort" in code else ("moyen" if "moyen" in code else "faible")
                            naturels["retrait_gonflement_argile"] = {"present": True, "level": level}
                        return GeorisquesResult(
                            risks={
                                "naturels": naturels,
                                "technologiques": _empty_techno_risks(),
                                "natural_risk_count": 1,
                                "techno_risk_count": 0,
                            },
                            commune=data.get("commune"),
                            commune_code=data.get("codeInsee"),
                            enrichment={
                                "argile_exposition": [{"code": 1, "label": str(data.get("alea", ""))}]
                                if data.get("alea") else None,
                                "cavities_nearby": None,
                                "polluted_sites_nearby": None,
                            },
                            source="v2",
                        )
            except Exception:
                pass  # Fallback to v1

        # Fallback: v1 public API (no token required)
        try:
            async with httpx.AsyncClient(timeout=CLIENT_TIMEOUT) as client:
                res = await client.get(
                    f"https://georisques.gouv.fr/api/v1/gaspar/risques?latlon={lat},{lon}",
                    headers={"Accept": "application/json"},
                )
                if res.is_success:
                    data = res.json()
                    naturels = _empty_natural_risks()
                    technologiques = _empty_techno_risks()
                    nat_count = 0
                    tech_count = 0

                    risques_naturels = data.get("risques_naturels", [])
                    if isinstance(risques_naturels, list):
                        nat_count = len(risques_naturels)
                        for r in risques_naturels:
                            lib = (r.get("libelle_risque", "") or "").lower()
                            if "inondation" in lib:
                                naturels["inondation"] = {"present": True, "level": "moyen"}
                            if "séisme" in lib or "seisme" in lib:
                                naturels["seisme"] = {"present": True, "level": "faible"}
                            if "argile" in lib:
                                naturels["retrait_gonflement_argile"] = {"present": True, "level": "moyen"}
                            if "feu" in lib or "forêt" in lib or "foret" in lib:
                                naturels["feu_foret"] = {"present": True, "level": "moyen"}

                    commune = data.get("commune", {})
                    return GeorisquesResult(
                        risks={
                            "naturels": naturels,
                            "technologiques": technologiques,
                            "natural_risk_count": nat_count,
                            "techno_risk_count": tech_count,
                        },
                        commune=commune.get("libelle_commune") if isinstance(commune, dict) else None,
                        commune_code=commune.get("code_insee") if isinstance(commune, dict) else None,
                        enrichment=None,
                        source="v1",
                    )
        except Exception:
            pass

        # Empty fallback
        return GeorisquesResult(
            risks={
                "naturels": _empty_natural_risks(),
                "technologiques": _empty_techno_risks(),
                "natural_risk_count": 0,
                "techno_risk_count": 0,
            },
            commune=None,
            commune_code=None,
            enrichment=None,
            source="v1",
        )
