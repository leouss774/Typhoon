"""
Supabase Auth — Local JWT Verification
=======================================
Verifies Supabase Auth JWTs locally using the SUPABASE_JWT_SECRET
and python-jose (already installed).

No need for the `supabase-py` package — Supabase Auth JWTs are
standard HS256 JWTs that python-jose can decode directly.

Usage:
    from core.supabase import verify_supabase_jwt
    user = verify_supabase_jwt(token)
    if user:
        print(f"Authenticated as {user['email']}")
"""

from __future__ import annotations

from typing import Any

from jose import JWTError, jwt

from core.config import settings


def verify_supabase_jwt(token: str) -> dict[str, Any] | None:
    """
    Verify a Supabase Auth JWT token locally.

    Supabase Auth issues standard HS256 JWTs with the following payload:
    {
        "sub": "user-uuid",          # User ID
        "email": "user@example.com",
        "role": "authenticated",      # Supabase role
        "aud": "authenticated",
        "exp": 1234567890,
        "iat": 1234567890
    }

    Uses the SUPABASE_JWT_SECRET from settings to verify the signature.

    Returns a normalized dict with 'sub', 'email', 'role' or None if invalid.
    """
    if not settings.SUPABASE_JWT_SECRET:
        return None

    try:
        payload = jwt.decode(
            token,
            settings.SUPABASE_JWT_SECRET,
            algorithms=["HS256"],
            options={"verify_aud": False},  # Allow both authenticated and anon audiences
        )
        return {
            "sub": payload.get("sub", ""),
            "email": payload.get("email", ""),
            "role": payload.get("role", "assureur"),
            "user_metadata": payload.get("user_metadata", {}),
        }
    except JWTError:
        return None
