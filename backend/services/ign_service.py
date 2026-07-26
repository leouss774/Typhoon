"""
IGN Altimetry & Open-Meteo Climate Services
============================================
Direct port of `backend/services/ign.service.ts`.
"""

from __future__ import annotations

from typing import Any

import httpx

CLIENT_TIMEOUT = 15.0


def _empty_climate() -> dict[str, Any]:
    return {
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


class IgnService:
    """Fetch altitude and climate data from IGN and Open-Meteo APIs."""

    @staticmethod
    async def fetch_altitude(lon: float, lat: float) -> dict[str, Any]:
        """
        Returns: { altitude: float | None, slope: 'flat' | 'moderate' | 'steep' | None }
        """
        try:
            async with httpx.AsyncClient(timeout=CLIENT_TIMEOUT) as client:
                url = (
                    "https://data.geopf.fr/altimetrie/1.0/calcul/alti/rest/elevation.json"
                    f"?lon={lon}&lat={lat}&resource=ign_rge_alti_wld"
                )
                res = await client.get(url)
                if not res.is_success:
                    return {"altitude": None, "slope": None}
                data = res.json()
                elevations = data.get("elevations", [])
                elev = elevations[0].get("z") if elevations else None
                if elev is None:
                    return {"altitude": None, "slope": None}
                slope = "flat" if elev < 10 else ("moderate" if elev < 100 else "steep")
                return {"altitude": float(elev), "slope": slope}
        except Exception:
            return {"altitude": None, "slope": None}

    @staticmethod
    async def fetch_climate(lon: float, lat: float) -> dict[str, Any]:
        """
        Fetch historical (2000-2014) and projected (2040-2050) climate data
        from Open-Meteo Climate API (CMIP6, EC_Earth3P_HR model).
        """
        try:
            async with httpx.AsyncClient(timeout=25.0) as client:
                url = (
                    f"https://climate-api.open-meteo.com/v1/climate"
                    f"?latitude={lat}&longitude={lon}"
                    f"&start_date=1950-01-01&end_date=2050-01-01"
                    f"&daily=temperature_2m_min,temperature_2m_max,precipitation_sum,"
                    f"wind_speed_10m_max,relative_humidity_2m_mean,"
                    f"relative_humidity_2m_max,relative_humidity_2m_min,"
                    f"soil_moisture_0_to_10cm_mean"
                    f"&models=EC_Earth3P_HR"
                )
                res = await client.get(url)
                if not res.is_success:
                    return _empty_climate()
                data = res.json()
                days = data.get("daily")
                if not days or not days.get("time"):
                    return _empty_climate()

                times: list[str] = days["time"]
                temps_min: list[float] = days.get("temperature_2m_min", [])
                temps_max: list[float] = days.get("temperature_2m_max", [])
                precip: list[float | None] = days.get("precipitation_sum", [])
                winds: list[float | None] = days.get("wind_speed_10m_max", [])
                humid_mean: list[float | None] = days.get("relative_humidity_2m_mean", [])
                humid_max: list[float | None] = days.get("relative_humidity_2m_max", [])
                humid_min: list[float | None] = days.get("relative_humidity_2m_min", [])
                soil_moist: list[float | None] = days.get("soil_moisture_0_to_10cm_mean", [])

                # Masks
                historical_mask = [
                    t >= "2000-01-01" and t <= "2014-12-31" for t in times
                ]
                projection_mask = [
                    t >= "2040-01-01" and t <= "2050-12-31" for t in times
                ]

                def compute_stats(mask: list[bool]) -> dict | None:
                    days_in_period = sum(1 for m in mask if m)
                    if days_in_period < 30:
                        return None
                    freeze = sum(1 for i, m in enumerate(mask) if m and temps_min[i] < 0)
                    heatwave = sum(1 for i, m in enumerate(mask) if m and temps_max[i] > 35)
                    total_precip = sum(
                        (precip[i] or 0) for i, m in enumerate(mask) if m
                    )
                    max_wind = max(
                        (winds[i] or 0) for i, m in enumerate(mask) if m and winds[i] is not None
                    )
                    return {
                        "freeze_per_year": round((freeze / days_in_period) * 365),
                        "heatwave_per_year": round((heatwave / days_in_period) * 365),
                        "annual_precip": round((total_precip / days_in_period) * 365),
                        "max_wind": max_wind,
                    }

                historical = compute_stats(historical_mask)
                projected = compute_stats(projection_mask)

                def compute_average(
                    mask: list[bool], values: list[float | None]
                ) -> float | None:
                    filtered = [v for i, v in enumerate(values) if mask[i] and v is not None]
                    if len(filtered) < 30:
                        return None
                    return sum(filtered) / len(filtered)

                hist_humid_mean = compute_average(historical_mask, humid_mean)
                hist_humid_max = compute_average(historical_mask, humid_max)
                hist_humid_min = compute_average(historical_mask, humid_min)
                hist_soil_moist = compute_average(historical_mask, soil_moist)
                proj_soil_moist = compute_average(projection_mask, soil_moist)

                def wind_to_storm(max_wind: float) -> int:
                    if max_wind > 100:
                        return 4
                    if max_wind > 80:
                        return 3
                    if max_wind > 60:
                        return 2
                    return 1

                # Determine snow zone (simplified from French zoning)
                snow_zone = "A1"

                return {
                    "freeze_days_per_year": historical["freeze_per_year"] if historical else None,
                    "storm_frequency": wind_to_storm(historical["max_wind"]) if historical else None,
                    "hail_risk": 1,
                    "annual_precipitation": historical["annual_precip"] if historical else None,
                    "heatwave_days_per_year": historical["heatwave_per_year"] if historical else None,
                    "wind_zone": wind_to_storm(historical["max_wind"]) if historical else None,
                    "snow_zone": snow_zone,
                    "projected_freeze_days": projected["freeze_per_year"] if projected else None,
                    "projected_heatwave_days": projected["heatwave_per_year"] if projected else None,
                    "projected_precipitation": projected["annual_precip"] if projected else None,
                    "projected_storm_frequency": wind_to_storm(projected["max_wind"]) if projected else None,
                    "projection_model": "EC_Earth3P_HR" if projected else None,
                    "projection_scenario": "CMIP6 high-resolution (≈RCP8.5)" if projected else None,
                    "mean_humidity": round(hist_humid_mean) if hist_humid_mean is not None else None,
                    "max_humidity": round(hist_humid_max) if hist_humid_max is not None else None,
                    "min_humidity": round(hist_humid_min) if hist_humid_min is not None else None,
                    "soil_moisture": (
                        round(hist_soil_moist * 1000) / 1000
                        if hist_soil_moist is not None
                        else None
                    ),
                    "projected_soil_moisture": (
                        round(proj_soil_moist * 1000) / 1000
                        if proj_soil_moist is not None
                        else None
                    ),
                }
        except Exception:
            return _empty_climate()
