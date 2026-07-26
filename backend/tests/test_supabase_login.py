"""
Tests for POST /api/auth/supabase-login
=========================================
Verifies the Supabase access token exchange flow.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from jose import jwt

from core.config import settings


@pytest.mark.skipif(
    not settings.SUPABASE_JWT_SECRET,
    reason="SUPABASE_JWT_SECRET not configured",
)
class TestSupabaseLogin:
    """Test the Supabase access token exchange endpoint."""

    def test_supabase_login_creates_user(self, client: TestClient) -> None:
        """A valid Supabase JWT should create a local user and set a cookie."""
        # Build a fake Supabase Auth JWT
        token = jwt.encode(
            {
                "sub": "test-supabase-uuid-123",
                "email": "alice@supabase.com",
                "role": "authenticated",
                "aud": "authenticated",
                "user_metadata": {"full_name": "Alice Supabase"},
            },
            settings.SUPABASE_JWT_SECRET,
            algorithm="HS256",
        )

        resp = client.post("/api/auth/supabase-login", json={"access_token": token})
        assert resp.status_code == 200, resp.text

        data = resp.json()
        assert data["user"]["email"] == "alice@supabase.com"
        assert data["user"]["first_name"] == "Alice"
        assert data["user"]["role"] == "assureur"

        # Cookie should be set
        set_cookie = resp.headers.get("set-cookie", "")
        assert "token=" in set_cookie
        assert "HttpOnly" in set_cookie

    def test_supabase_login_existing_user(self, client: TestClient) -> None:
        """If the user already exists, it should re-login them."""
        # First call — creates the user
        token = jwt.encode(
            {
                "sub": "test-supabase-uuid-456",
                "email": "bob@supabase.com",
                "role": "authenticated",
                "user_metadata": {"full_name": "Bob Supabase"},
            },
            settings.SUPABASE_JWT_SECRET,
            algorithm="HS256",
        )

        resp1 = client.post("/api/auth/supabase-login", json={"access_token": token})
        assert resp1.status_code == 200
        user_id = resp1.json()["user"]["id"]

        # Second call — same user, should not duplicate
        resp2 = client.post("/api/auth/supabase-login", json={"access_token": token})
        assert resp2.status_code == 200
        assert resp2.json()["user"]["id"] == user_id

    def test_supabase_login_invalid_token(self, client: TestClient) -> None:
        """An invalid Supabase JWT should return 401."""
        resp = client.post(
            "/api/auth/supabase-login",
            json={"access_token": "this-is-not-a-valid-jwt"},
        )
        assert resp.status_code == 401

    def test_supabase_login_missing_token(self, client: TestClient) -> None:
        """Missing access_token should return 422 (Pydantic validation)."""
        resp = client.post("/api/auth/supabase-login", json={})
        assert resp.status_code == 422
