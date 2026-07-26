"""
24-hour In-Memory Assessment Cache
===================================
Direct port of `backend/services/cache.service.ts`.
"""

from __future__ import annotations

import time
from typing import Any


class AssessmentCache:
    """In-memory cache for risk assessment results with 24h TTL."""

    _TTL_MS: int = 24 * 60 * 60 * 1000  # 24 hours
    _cache: dict[str, tuple[float, Any]] = {}  # key -> (timestamp, data)

    @staticmethod
    def _make_key(lat: float, lon: float) -> str:
        return f"{lat:.3f},{lon:.3f}"

    @staticmethod
    def get(lat: float, lon: float) -> Any | None:
        key = AssessmentCache._make_key(lat, lon)
        entry = AssessmentCache._cache.get(key)
        if entry is None:
            return None
        timestamp, data = entry
        if (time.time() * 1000 - timestamp) > AssessmentCache._TTL_MS:
            del AssessmentCache._cache[key]
            return None
        return data

    @staticmethod
    def set(lat: float, lon: float, data: Any) -> None:
        key = AssessmentCache._make_key(lat, lon)
        AssessmentCache._cache[key] = (time.time() * 1000, data)
