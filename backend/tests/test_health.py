"""
Health Check Tests
==================
"""

from __future__ import annotations

from fastapi.testclient import TestClient


class TestHealth:
    """Test the /health endpoint."""

    def test_health_returns_ok(self, client: TestClient) -> None:
        response = client.get("/health")
        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "ok"
        assert "timestamp" in body
