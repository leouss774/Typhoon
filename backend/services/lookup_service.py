"""
Lookup Service — DVF (valuation) + DRIAS (climate) by department
=================================================================
Direct port of `backend/services/lookup.service.ts`.

Both providers have no public REST API. DVF is published as CSV files
on data.gouv.fr, DRIAS as NetCDF files on the DRIAS portal.
We pre-load the most populated departments and serve them from JSON.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

_DATA_DIR = Path(__file__).resolve().parent.parent / "data"

_departments_cache: dict[str, Any] | None = None
_drias_cache: dict[str, Any] | None = None


def _load_json(filename: str) -> Any:
    path = _DATA_DIR / filename
    if not path.exists():
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _get_departments() -> Any:
    global _departments_cache
    if _departments_cache is None:
        _departments_cache = _load_json("departments.json")
    return _departments_cache


def _get_drias() -> Any:
    global _drias_cache
    if _drias_cache is None:
        _drias_cache = _load_json("drias.json")
    return _drias_cache


class DvfLookupResult:
    """Department-level DVF averages."""

    def __init__(self, reconstruction_value_per_sqm: float | None, last_transaction_price_per_sqm: float | None):
        self.reconstruction_value_per_sqm = reconstruction_value_per_sqm
        self.last_transaction_price_per_sqm = last_transaction_price_per_sqm


class DriasDepartmentData:
    """DRIAS ADAMONT-corrected climate indicators per department."""

    def __init__(
        self,
        heatwave_days: int,
        tropical_nights: int,
        summer_days: int,
        heavy_precip_days: int,
        max5day_precip: float,
        consecutive_dry_days: int,
        fire_weather_index: float,
        frost_days: int,
        data_source: str,
        data_confidence: str,
    ):
        self.heatwave_days = heatwave_days
        self.tropical_nights = tropical_nights
        self.summer_days = summer_days
        self.heavy_precip_days = heavy_precip_days
        self.max5day_precip = max5day_precip
        self.consecutive_dry_days = consecutive_dry_days
        self.fire_weather_index = fire_weather_index
        self.frost_days = frost_days
        self.data_source = data_source
        self.data_confidence = data_confidence


class DriasLookupResult:
    """DRIAS lookup with metadata."""

    def __init__(self, drias: DriasDepartmentData, method: str, warming_level: str):
        self.drias = drias
        self.method = method
        self.warming_level = warming_level


class LookupService:
    """Static methods for DVF and DRIAS lookups."""

    @staticmethod
    def lookup_dvf(dept_code: str) -> DvfLookupResult | None:
        """Look up DVF valuation data by department INSEE code."""
        data = _get_departments()
        if not data:
            return None
        dept = data.get("departments", {}).get(dept_code)
        if not dept or "valuation" not in dept:
            return None
        val = dept["valuation"]
        return DvfLookupResult(
            reconstruction_value_per_sqm=val.get("reconstructionValuePerSqm"),
            last_transaction_price_per_sqm=val.get("avgMarketPricePerSqm"),
        )

    @staticmethod
    def lookup_drias(dept_code: str) -> DriasLookupResult | None:
        """Look up DRIAS climate indicators by department INSEE code."""
        data = _get_drias()
        if not data:
            return None
        dept = data.get("departments", {}).get(dept_code)
        if not dept or "drias" not in dept:
            return None
        d = dept["drias"]
        drias = DriasDepartmentData(
            heatwave_days=d.get("heatwaveDays", 0),
            tropical_nights=d.get("tropicalNights", 0),
            summer_days=d.get("summerDays", 0),
            heavy_precip_days=d.get("heavyPrecipDays", 0),
            max5day_precip=d.get("max5dayPrecip", 0),
            consecutive_dry_days=d.get("consecutiveDryDays", 0),
            fire_weather_index=d.get("fireWeatherIndex", 0),
            frost_days=d.get("frostDaysDrias", 0),
            data_source=d.get("dataSource", ""),
            data_confidence=d.get("dataConfidence", "medium"),
        )
        return DriasLookupResult(
            drias=drias,
            method=data.get("method", "ADAMONT"),
            warming_level=data.get("warmingLevel", "+4°C France (TRACC horizon 2050)"),
        )
