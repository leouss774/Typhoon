"""
Auth Tests — Register, Login, Logout, Me
=========================================
"""

from __future__ import annotations

from fastapi.testclient import TestClient


class TestAuth:
    """Test auth endpoints."""

    def test_register(self, client: TestClient) -> None:
        response = client.post(
            "/api/auth/register",
            json={
                "email": "test@example.fr",
                "password": "Password123!",
                "first_name": "Jean",
                "last_name": "Test",
                "role": "assureur",
            },
        )
        assert response.status_code == 201
        body = response.json()
        assert body["user"]["email"] == "test@example.fr"
        assert body["user"]["first_name"] == "Jean"
        assert "Set-Cookie" in response.headers

    def test_register_duplicate_email(self, client: TestClient) -> None:
        client.post(
            "/api/auth/register",
            json={
                "email": "dup@example.fr",
                "password": "Password123!",
                "first_name": "Jean",
                "last_name": "Dupont",
            },
        )
        response = client.post(
            "/api/auth/register",
            json={
                "email": "dup@example.fr",
                "password": "Password123!",
                "first_name": "Jean",
                "last_name": "Dupont",
            },
        )
        assert response.status_code == 409

    def test_login(self, client: TestClient) -> None:
        # Register first
        client.post(
            "/api/auth/register",
            json={
                "email": "login@example.fr",
                "password": "Password123!",
                "first_name": "Jean",
                "last_name": "Login",
            },
        )
        # Login
        response = client.post(
            "/api/auth/login",
            json={"email": "login@example.fr", "password": "Password123!"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["user"]["email"] == "login@example.fr"
        assert "Set-Cookie" in response.headers

    def test_login_invalid_credentials(self, client: TestClient) -> None:
        response = client.post(
            "/api/auth/login",
            json={"email": "nonexistent@example.fr", "password": "wrong"},
        )
        assert response.status_code == 401

    def test_me_authenticated(self, client: TestClient) -> None:
        # Register and extract cookie
        reg_resp = client.post(
            "/api/auth/register",
            json={
                "email": "me@example.fr",
                "password": "Password123!",
                "first_name": "Test",
                "last_name": "Me",
            },
        )
        cookie = reg_resp.headers.get("Set-Cookie", "")

        # Use cookie to access /me
        response = client.get("/api/auth/me", headers={"Cookie": cookie})
        assert response.status_code == 200
        assert response.json()["user"]["email"] == "me@example.fr"

    def test_me_unauthenticated(self, client: TestClient) -> None:
        response = client.get("/api/auth/me")
        assert response.status_code == 401

    def test_logout(self, client: TestClient) -> None:
        response = client.post("/api/auth/logout")
        assert response.status_code == 200
        assert "Max-Age=0" in response.headers.get("Set-Cookie", "")
