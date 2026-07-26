"""
IGN WFS Distance Queries — Waterway + Forest
=============================================
Direct port of `backend/services/wfs.service.ts`.

Fetches minimum distance from a coordinate point to:
  - Waterway (BD TOPO V3: troncon_hydrographique + surface_hydrographique)
  - Forest (Masque Forêt IGN 2021-2023)
"""

from __future__ import annotations

import math
from typing import Any

import httpx

CLIENT_TIMEOUT = 8.0


def _haversine(lon1: float, lat1: float, lon2: float, lat2: float) -> float:
    """Haversine distance between two lon/lat points in metres."""
    R = 6371000
    d_lon = math.radians(lon2 - lon1)
    d_lat = math.radians(lat2 - lat1)
    a = (
        math.sin(d_lat / 2) ** 2
        + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(d_lon / 2) ** 2
    )
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def _min_distance_to_geometry(lon: float, lat: float, geom: dict[str, Any]) -> float | None:
    """Compute minimum distance from (lon, lat) to a GeoJSON geometry."""
    if not geom or not geom.get("type") or not geom.get("coordinates"):
        return None

    def extract_coords(coords: Any, geom_type: str) -> list[tuple[float, float]]:
        if geom_type == "Point":
            return [(coords[0], coords[1])]
        if geom_type in ("MultiPoint", "LineString"):
            return [(c[0], c[1]) for c in coords]
        if geom_type in ("MultiLineString", "Polygon"):
            return [(c[0], c[1]) for ring in coords for c in ring]
        if geom_type == "MultiPolygon":
            return [(c[0], c[1]) for polygon in coords for ring in polygon for c in ring]
        return []

    points = extract_coords(geom["coordinates"], geom["type"])
    if not points:
        return None

    min_dist = float("inf")
    for plon, plat in points:
        d = _haversine(lon, lat, plon, plat)
        if d < min_dist:
            min_dist = d
    return round(min_dist) if min_dist != float("inf") else None


class WfsService:
    """Fetch distance to waterway and forest from IGN WFS."""

    @staticmethod
    async def fetch_waterway_distance(lon: float, lat: float) -> float | None:
        """Minimum distance to nearest waterway (in metres)."""
        bbox = f"{lat - 0.05},{lon - 0.05},{lat + 0.05},{lon + 0.05}"
        min_dist = float("inf")

        type_names = [
            "BDTOPO_V3:troncon_hydrographique",
            "BDTOPO_V3:surface_hydrographique",
        ]

        async with httpx.AsyncClient(timeout=CLIENT_TIMEOUT) as client:
            for type_name in type_names:
                try:
                    url = (
                        "https://data.geopf.fr/wfs/ows?service=WFS&version=2.0.0"
                        f"&request=GetFeature&typeNames={type_name}&bbox={bbox}"
                        "&outputFormat=application/json&count=50"
                    )
                    res = await client.get(url, headers={"Accept": "application/json"})
                    if not res.is_success:
                        continue
                    data = res.json()
                    features = data.get("features", [])
                    for feature in features:
                        d = _min_distance_to_geometry(lon, lat, feature.get("geometry", {}))
                        if d is not None and d < min_dist:
                            min_dist = d
                except Exception:
                    continue

        return min_dist if min_dist != float("inf") else None

    @staticmethod
    async def fetch_forest_distance(lon: float, lat: float) -> float | None:
        """Minimum distance to nearest forest (in metres)."""
        bbox = f"{lat - 0.05},{lon - 0.05},{lat + 0.05},{lon + 0.05}"
        min_dist = float("inf")

        try:
            async with httpx.AsyncClient(timeout=CLIENT_TIMEOUT) as client:
                url = (
                    "https://data.geopf.fr/wfs/ows?service=WFS&version=2.0.0"
                    "&request=GetFeature"
                    "&typeNames=IGNF_MASQUE-FORET.2021-2023:masque_foret"
                    f"&bbox={bbox}"
                    "&outputFormat=application/json&count=50"
                )
                res = await client.get(url, headers={"Accept": "application/json"})
                if res.is_success:
                    data = res.json()
                    features = data.get("features", [])
                    for feature in features:
                        if feature.get("properties", {}).get("nature") != "Forêt":
                            continue
                        d = _min_distance_to_geometry(lon, lat, feature.get("geometry", {}))
                        if d is not None and d < min_dist:
                            min_dist = d
        except Exception:
            pass

        return min_dist if min_dist != float("inf") else None
