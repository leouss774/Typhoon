"""
User Context — Normalized Auth User
====================================
Both custom JWT authentication and Supabase Auth return user data in
slightly different shapes. This class normalizes them so route handlers
can always use `user.sub`, `user.email`, and `user.role` consistently.

Supports both attribute access (user.sub) and dict access (user["sub"]).
"""

from __future__ import annotations

from typing import Any


class UserContext:
    """
    Normalized user identity injected by the auth middleware.
    Works identically whether the user was authenticated via:
    - Custom JWT (POST /api/auth/login) → JwtPayload
    - Supabase Auth (Authorization: Bearer) → dict from Supabase JWT
    """

    def __init__(self, sub: str, email: str, role: str, metadata: dict[str, Any] | None = None) -> None:
        self.sub = sub
        self.email = email
        self.role = role
        self.metadata = metadata or {}

    def __getitem__(self, key: str) -> Any:
        return getattr(self, key)

    @classmethod
    def from_jwt_payload(cls, payload: Any) -> UserContext:
        """Create from a JwtPayload object (custom JWT)."""
        return cls(sub=payload.sub, email=payload.email, role=payload.role)

    @classmethod
    def from_supabase_dict(cls, data: dict[str, Any]) -> UserContext:
        """Create from a Supabase JWT verification result dict."""
        return cls(
            sub=data.get("sub", ""),
            email=data.get("email", ""),
            role=data.get("role", "assureur"),
            metadata=data.get("user_metadata", {}),
        )
