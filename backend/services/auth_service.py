"""
Auth Service — JWT via httpOnly cookies + bcrypt password hashing
=================================================================
Direct port of `backend/services/auth.service.ts`.
"""

from __future__ import annotations

import re

from core.security import (
    JwtPayload,
    build_cookie_value,
    clear_cookie_value,
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


class AuthService:
    """
    Authentication logic.
    Delegates to `core/security.py` for crypto primitives.
    """

    @staticmethod
    def hash_password(password: str) -> str:
        return hash_password(password)

    @staticmethod
    def verify_password(plain: str, hashed: str) -> bool:
        return verify_password(plain, hashed)

    @staticmethod
    def create_token(user_id: str, email: str, role: str) -> str:
        payload = JwtPayload(sub=user_id, email=email, role=role)  # type: ignore
        return create_access_token(payload)

    @staticmethod
    def verify_token(token: str) -> JwtPayload | None:
        return decode_access_token(token)

    @staticmethod
    def build_cookie(token: str) -> str:
        return build_cookie_value(token)

    @staticmethod
    def clear_cookie() -> str:
        return clear_cookie_value()

    @staticmethod
    def extract_token_from_cookie(cookie_header: str | None) -> str | None:
        """Parse JWT token from the `token` cookie."""
        if not cookie_header:
            return None
        match = re.search(r"(?:^|;\s*)token=([^;]*)", cookie_header)
        return match.group(1) if match else None
