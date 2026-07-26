"""
Scoring Engine Service
======================
Direct port of `backend/services/scoring.service.ts`.
All formulas, weights, and thresholds are preserved exactly.

Risk perils:
  - Inondation (30%)
  - RGA — Retrait-Gonflement Argiles (25%)
  - Tempête (20%)
  - Incendie — Feu de forêt (15%)
  - Séisme (10%)

Each function independently computes a 0–100 score.
The global score is a weighted composite.
"""

from __future__ import annotations

import math
from typing import Any


class ScoringEngine:
    """
    Computes peril scores and a weighted global score from a
    full RiskAssessmentInput dict.
    """

    # Global weights matching the TypeScript constants
    GLOBAL_WEIGHTS = {
        "inondation": 0.30,
        "rga": 0.25,
        "tempete": 0.20,
        "incendie": 0.15,
        "seisme": 0.10,
    }

    @staticmethod
    def _level_to_severity(level: str | None) -> int:
        mapping = {
            "tres_fort": 90,
            "fort": 70,
            "moyen": 40,
            "faible": 15,
        }
        return mapping.get(level, 0) if level else 0

    @staticmethod
    def _clamp(n: float) -> int:
        return max(0, min(100, round(n)))

    @staticmethod
    def _proximity_score(distance: float | None, max_dist: float) -> int:
        if distance is None:
            return 0
        if distance >= max_dist:
            return 0
        return round((1 - distance / max_dist) * 100)

    @staticmethod
    def _score_inondation(assessment: dict[str, Any]) -> int:
        naturels = assessment.get("risks", {}).get("naturels", {})
        inondation = naturels.get("inondation", {})
        geography = assessment.get("geography", {})

        water_dist = geography.get("distance_to_waterway")
        altitude = geography.get("altitude")

        georisque_score = (
            max(ScoringEngine._level_to_severity(inondation.get("level")), 25)
            if inondation.get("present", False)
            else 0
        )
        water_score = ScoringEngine._proximity_score(water_dist, 1000)

        altitude_score = 0
        if altitude is not None:
            if altitude < 10:
                altitude_score = 70
            elif altitude < 30:
                altitude_score = 40
            elif altitude < 50:
                altitude_score = 20
            else:
                altitude_score = 5

        return ScoringEngine._clamp(
            georisque_score * 0.40 + water_score * 0.30 + altitude_score * 0.30
        )

    @staticmethod
    def _score_rga(assessment: dict[str, Any]) -> int:
        naturels = assessment.get("risks", {}).get("naturels", {})
        rga = naturels.get("retrait_gonflement_argile", {})
        climate = assessment.get("climate", {})
        prop = assessment.get("property", {})

        soil_moisture = climate.get("soil_moisture")
        clay_exposure = prop.get("clay_exposure")

        rga_score = (
            max(ScoringEngine._level_to_severity(rga.get("level")), 20)
            if rga.get("present", False)
            else 0
        )

        moisture_score = 15
        if soil_moisture is not None:
            if soil_moisture < 0.15:
                moisture_score = 60
            elif soil_moisture < 0.25:
                moisture_score = 40
            elif soil_moisture < 0.35:
                moisture_score = 20
            else:
                moisture_score = 5

        bdnb_clay_score = 0
        if clay_exposure:
            upper = clay_exposure.upper()
            if "FORT" in upper:
                bdnb_clay_score = 70
            elif "MOYEN" in upper:
                bdnb_clay_score = 40
            elif "FAIBLE" in upper:
                bdnb_clay_score = 15

        return ScoringEngine._clamp(
            rga_score * 0.50 + moisture_score * 0.25 + bdnb_clay_score * 0.25
        )

    @staticmethod
    def _score_tempete(assessment: dict[str, Any]) -> int:
        climate = assessment.get("climate", {})
        naturels = assessment.get("risks", {}).get("naturels", {})
        cyclone = naturels.get("cyclone", {})

        wind_zone = climate.get("wind_zone")
        storm_freq = climate.get("storm_frequency")

        wind_score = 0
        if wind_zone is not None:
            if wind_zone <= 1:
                wind_score = 10
            elif wind_zone == 2:
                wind_score = 30
            elif wind_zone == 3:
                wind_score = 55
            elif wind_zone >= 4:
                wind_score = 80

        storm_score = 0
        if storm_freq is not None:
            if storm_freq <= 1:
                storm_score = 10
            elif storm_freq == 2:
                storm_score = 30
            elif storm_freq == 3:
                storm_score = 55
            elif storm_freq >= 4:
                storm_score = 80

        cyclone_score = 60 if cyclone.get("present", False) else 0

        return ScoringEngine._clamp(
            wind_score * 0.40 + storm_score * 0.40 + cyclone_score * 0.20
        )

    @staticmethod
    def _score_incendie(assessment: dict[str, Any]) -> int:
        naturels = assessment.get("risks", {}).get("naturels", {})
        feu_foret = naturels.get("feu_foret", {})
        climate = assessment.get("climate", {})
        geography = assessment.get("geography", {})

        if not feu_foret.get("present", False):
            return 0

        feu_score = ScoringEngine._level_to_severity(feu_foret.get("level")) or 30

        drias = climate.get("drias", {})
        fwi = drias.get("fire_weather_index")
        fwi_score = 15
        if fwi is not None:
            if fwi >= 50:
                fwi_score = 80
            elif fwi >= 35:
                fwi_score = 55
            elif fwi >= 20:
                fwi_score = 30
            elif fwi >= 10:
                fwi_score = 15
            else:
                fwi_score = 5

        forest_dist = geography.get("distance_to_forest")
        forest_score = ScoringEngine._proximity_score(forest_dist, 2000)

        return ScoringEngine._clamp(feu_score * 0.40 + fwi_score * 0.30 + forest_score * 0.30)

    @staticmethod
    def _score_seisme(assessment: dict[str, Any]) -> int:
        naturels = assessment.get("risks", {}).get("naturels", {})
        seisme = naturels.get("seisme", {})
        if not seisme.get("present", False):
            return 0
        return ScoringEngine._clamp(
            float(ScoringEngine._level_to_severity(seisme.get("level")))
        )

    @staticmethod
    def score_all(assessment: dict[str, Any]) -> dict[str, int]:
        """
        Compute all peril scores + global.
        Returns dict with keys: inondation, rga, tempete, incendie, seisme, global_score
        """
        scores = {
            "inondation": ScoringEngine._score_inondation(assessment),
            "rga": ScoringEngine._score_rga(assessment),
            "tempete": ScoringEngine._score_tempete(assessment),
            "incendie": ScoringEngine._score_incendie(assessment),
            "seisme": ScoringEngine._score_seisme(assessment),
        }

        global_score = ScoringEngine._clamp(
            scores["inondation"] * ScoringEngine.GLOBAL_WEIGHTS["inondation"]
            + scores["rga"] * ScoringEngine.GLOBAL_WEIGHTS["rga"]
            + scores["tempete"] * ScoringEngine.GLOBAL_WEIGHTS["tempete"]
            + scores["incendie"] * ScoringEngine.GLOBAL_WEIGHTS["incendie"]
            + scores["seisme"] * ScoringEngine.GLOBAL_WEIGHTS["seisme"]
        )

        scores["global_score"] = global_score
        return scores
