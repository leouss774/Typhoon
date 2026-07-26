"""
Supabase Auth Tests
===================
Tests the Authorization: Bearer <token> auth flow.
Verifies that the backend properly validates Supabase Auth JWTs
when SUPABASE_JWT_SECRET is configured.

NOTE: These tests use the settings.SUPABASE_JWT_SECRET to sign
a test token locally (simulating what Supabase Auth would issue).
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient
from jose import jwt

from core.config import settings


@pytest.mark.skipif(
    not settings.SUPABASE_JWT_SECRET,
    reason="SUPABASE_JWT_SECRET not configured — skipping Supabase Auth tests",
)
class TestSupabaseAuth:
    """Test the Authorization: Bearer flow with Supabase-style JWTs."""

    def _create_supabase_token(self, sub: str = "test-user-uuid", email: str = "supa@test.fr") -> str:
        """Create a JWT mimicking what Supabase Auth would issue."""
        now = datetime.now(timezone.utc)
        payload = {
            "sub": sub,
            "email": email,
            "role": "authenticated",
            "aud": "authenticated",
            "iat": now,
            "exp": now + timedelta(hours=1),
        }
        return jwt.encode(payload, settings.SUPABASE_JWT_SECRET, algorithm="HS256")

    def test_bearer_token_authenticated(self, client: TestClient) -> None:
        """Authorization: Bearer with valid Supabase JWT should return user data."""
        token = self._create_supabase_token()
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["user"]["email"] == "supa@test.fr"

    def test_bearer_token_invalid(self, client: TestClient) -> None:
        """Invalid Bearer token should return 401."""
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": "Bearer invalid-token"},
        )
        assert response.status_code == 401

    def test_bearer_token_expired(self, client: TestClient) -> None:
        """Expired token should return 401."""
        now = datetime.now(timezone.utc)
        payload = {
            "sub": "test-uuid",
            "email": "expired@test.fr",
            "role": "authenticated",
            "aud": "authenticated",
            "iat": now - timedelta(hours=2),
            "exp": now - timedelta(hours=1),
        }
        token = jwt.encode(payload, settings.SUPABASE_JWT_SECRET, algorithm="HS256")
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 401

    def test_bearer_token_no_email(self, client: TestClient) -> None:
        """Token without email should still authenticate (email may be empty)."""
        token = self._create_supabase_token(email="")
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200

    def test_bearer_has_priority_over_cookie(self, client: TestClient) -> None:
        """Bearer token should take priority over cookie-based auth."""
        # Register to get a valid cookie
        reg_resp = client.post(
            "/api/auth/register",
            json={
                "email": "cookieuser@test.fr",
                "password": "Password123!",
                "first_name": "Cookie",
                "last_name": "User",
            },
        )
        cookie = reg_resp.headers.get("Set-Cookie", "")

        # Now send request with both Bearer token and cookie
        supabase_token = self._create_supabase_token(email="supabase@test.fr")
        response = client.get(
            "/api/auth/me",
            headers={
                "Authorization": f"Bearer {supabase_token}",
                "Cookie": cookie,
            },
        )

        # Bearer should take priority — respond with Supabase user
        assert response.status_code == 200
        data = response.json()
        assert data["user"]["email"] == "supabase@test.fr"
