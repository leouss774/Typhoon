"""
BDNB Building Data Service — Server-side fetcher
=================================================
Direct port of `backend/services/bdnb.service.ts`.

Fetches building characteristics from the Base Nationale des Bâtiments (BDNB).
"""

from __future__ import annotations

from typing import Any

import httpx

CLIENT_TIMEOUT = 10.0


def _construction_period(year: int | None) -> str | None:
    if not year:
        return None
    if year < 1915:
        return "<1915"
    if year <= 1948:
        return "1915_1948"
    if year <= 1974:
        return "1949_1974"
    if year <= 2000:
        return "1975_2000"
    if year <= 2012:
        return "2001_2012"
    if year <= 2021:
        return "2013_2021"
    return ">2021"


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
        "footprint": None,
    }


class BdnbService:
    """Fetch building data from BDNB API."""

    @staticmethod
    async def fetch_building_by_ban_id(ban_id: str) -> dict[str, Any]:
        dept_code = ban_id[:2]
        empty = _empty_building(dept_code)

        try:
            async with httpx.AsyncClient(timeout=CLIENT_TIMEOUT) as client:
                # Step 1: resolve ban_id → batiment_groupe_id
                url = (
                    f"https://api.bdnb.io/v1/bdnb/donnees/rel_batiment_groupe_adresse"
                    f"?cle_interop_adr=eq.{ban_id}&select=batiment_groupe_id"
                )
                res = await client.get(url, headers={"Accept": "application/json"})
                if not res.is_success:
                    return empty

                rel_data = res.json()
                rel_list = rel_data if isinstance(rel_data, list) else []
                group_ids = [
                    r["batiment_groupe_id"]
                    for r in rel_list
                    if r.get("batiment_groupe_id")
                ]
                if not group_ids:
                    return empty

                # Step 2: fetch building details
                ids_param = ",".join(f'"{gid}"' for gid in group_ids)
                bdg_url = (
                    f"https://api.bdnb.io/v1/bdnb/donnees/batiment_groupe_complet"
                    f"?batiment_groupe_id=in.({ids_param})"
                )
                bdg_res = await client.get(bdg_url, headers={"Accept": "application/json"})
                if not bdg_res.is_success:
                    return empty

                bdg_data = bdg_res.json()
                arr = bdg_data if isinstance(bdg_data, list) else bdg_data.get("features", [])
                if not arr:
                    return empty

                props = arr[0].get("properties", arr[0])
                year = props.get("annee_construction") or None

                return {
                    "built_year": year,
                    "construction_period": _construction_period(year),
                    "surface_utile": props.get("surface_habitable"),
                    "surface_emprise": props.get("surface_emprise_sol"),
                    "levels": props.get("nb_niveau"),
                    "height": props.get("hauteur_mean") or props.get("hauteur"),
                    "dpe_class": props.get("classe_bilan_dpe"),
                    "energy_consumption": props.get("conso_energie"),
                    "emission_ges": props.get("emission_ges"),
                    "wall_material": (
                        props["mat_mur_txt"]
                        if props.get("mat_mur_txt") and props["mat_mur_txt"] != "INDETERMINE"
                        else None
                    ),
                    "roof_material": (
                        props["mat_toit_txt"]
                        if props.get("mat_toit_txt") and props["mat_toit_txt"] != "INDETERMINE"
                        else None
                    ),
                    "heating_type": (
                        props["etat_chauffage_txt"]
                        if props.get("etat_chauffage_txt") and props["etat_chauffage_txt"] != "INDETERMINE"
                        else None
                    ),
                    "usage_type": props.get("usage_principal_bdnb_open"),
                    "nb_logements": props.get("nb_logements"),
                    "department_code": dept_code,
                    "nb_logements_rnc": props.get("nb_log"),
                    "clay_exposure": (
                        props["alea_argile"]
                        if props.get("alea_argile") and props["alea_argile"] != "INDETERMINE"
                        else None
                    ),
                    "altitude_sol_mean": props.get("altitude_sol_mean"),
                    "heating_energy_type": props.get("type_energie_chauffage"),
                    "parcel_ids": (
                        props["l_parcelle_id"]
                        if isinstance(props.get("l_parcelle_id"), list)
                        else None
                    ),
                    "quartier_prioritaire": (
                        props.get("quartier_prioritaire") in (True, "true")
                    ),
                    "zone_patrimoniale": props.get("zone_plu_bati_patrimonial"),
                    "footprint": arr[0].get("geometry"),
                }
        except Exception:
            return empty
