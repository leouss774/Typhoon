"""
Security — JWT tokens and password hashing
==========================================
Port of the original `backend/services/auth.service.ts`:
- Hash and verify passwords with bcrypt
- Sign and verify JWT tokens (HS256)
- Build / clear httpOnly cookie headers

Key differences from TS version:
- Uses `python-jose` for JWT (equivalent to `jose` npm package)
- Uses `bcrypt` directly (no passlib wrapper — avoids compatibility issues)
- Cookie building is a string helper; actual cookie setting is via FastAPI's Response
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Literal

import bcrypt
from jose import JWTError, jwt

from core.config import settings

# ─── Password hashing ─────────────────────────────────────────────


def hash_password(password: str) -> str:
    """Hash a password with bcrypt (12 rounds)."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt(rounds=12)).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its bcrypt hash."""
    return bcrypt.checkpw(
        plain_password.encode("utf-8"), hashed_password.encode("utf-8")
    )


# ─── JWT ──────────────────────────────────────────────────────────

JwtRole = Literal["assureur", "assure"]


class JwtPayload:
    """Typed JWT payload matching the original `JwtPayload` interface."""

    def __init__(self, sub: str, email: str, role: JwtRole) -> None:
        self.sub = sub
        self.email = email
        self.role = role

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> JwtPayload:
        return cls(
            sub=str(data["sub"]),
            email=str(data["email"]),
            role=str(data["role"]),  # type: ignore[assignment]
        )

    def to_dict(self) -> dict[str, Any]:
        return {"sub": self.sub, "email": self.email, "role": self.role}


def create_access_token(payload: JwtPayload) -> str:
    """
    Sign a JWT access token.
    Equivalent to `signToken()` in the TS auth service.
    """
    to_encode = {
        **payload.to_dict(),
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc)
        + timedelta(hours=settings.JWT_EXPIRATION_HOURS),
    }
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm="HS256")


def decode_access_token(token: str) -> JwtPayload | None:
    """
    Verify and decode a JWT access token.
    Equivalent to `verifyToken()` in the TS auth service.
    Returns None if the token is invalid or expired.
    """
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
        return JwtPayload.from_dict(payload)
    except JWTError:
        return None


# ─── Cookie helpers ───────────────────────────────────────────────


def build_cookie_value(token: str) -> str:
    """
    Build the Set-Cookie header value for the auth token.
    Equivalent to `buildCookieHeader()` in TS.
    """
    max_age = settings.JWT_EXPIRATION_HOURS * 3600
    secure = "; Secure" if settings.COOKIE_SECURE else ""
    return (
        f"token={token}; HttpOnly; SameSite=Lax; Path=/; Max-Age={max_age}{secure}"
    )


def clear_cookie_value() -> str:
    """Build the Set-Cookie header value to clear the auth token."""
    return "token=; HttpOnly; SameSite=Lax; Path=/; Max-Age=0"
