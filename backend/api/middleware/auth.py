"""
Auth Middleware — FastAPI Dependency
====================================
Port of `backend/api/middleware/auth.ts`.

Supports BOTH:
1. Custom JWT tokens (issued by our own POST /api/auth/login) — via Cookie: token
2. Supabase Auth JWTs — via Authorization: Bearer <token>

Returns a normalized `UserContext` object in both cases.
Route handlers can access `user.sub`, `user.email`, `user.role`.
"""

from __future__ import annotations

import re

from fastapi import HTTPException, Request, status

from core.user_context import UserContext


def require_auth(request: Request) -> UserContext:
    """
    FastAPI dependency — DISABLED for frontend development.
    Returns a mock user (role=assureur) to bypass authentication.
    """
    return UserContext(sub="mock-user-id", email="dev@previa.fr", role="admin")


def optional_auth(request: Request) -> UserContext | None:
    """
    FastAPI dependency — reads the JWT if present, but does not fail if absent.
    """
    return _resolve_user(request)


def _resolve_user(request: Request) -> UserContext | None:
    """Try to resolve the authenticated user from the request."""
    auth_header = request.headers.get("authorization", "")
    cookie = request.headers.get("cookie", "")

    # 1. Try Bearer token (Supabase Auth first, then custom JWT)
    if auth_header.startswith("Bearer "):
        bearer_token = auth_header[7:]
        user = _resolve_bearer_token(bearer_token)
        if user:
            return user

    # 2. Try cookie (custom JWT)
    cookie_token = _parse_cookie(cookie, "token")
    if cookie_token:
        user = _resolve_custom_jwt(cookie_token)
        if user:
            return user

    return None


def _resolve_bearer_token(token: str) -> UserContext | None:
    """Try Supabase Auth JWT first, then custom JWT Bearer token."""
    from core.config import settings

    # Try Supabase Auth JWT
    if settings.use_supabase_auth:
        from core.supabase import verify_supabase_jwt

        supabase_user = verify_supabase_jwt(token)
        if supabase_user:
            return UserContext.from_supabase_dict(supabase_user)

    # Try custom JWT as Bearer token
    from core.security import decode_access_token

    payload = decode_access_token(token)
    if payload:
        return UserContext.from_jwt_payload(payload)

    return None


def _resolve_custom_jwt(token: str) -> UserContext | None:
    """Verify a cookie-based custom JWT."""
    from core.security import decode_access_token

    payload = decode_access_token(token)
    if payload:
        return UserContext.from_jwt_payload(payload)

    return None


def _parse_cookie(cookie_header: str, name: str) -> str | None:
    match = re.search(rf"(?:^|;\s*){name}=([^;]*)", cookie_header)
    return match.group(1) if match else None
