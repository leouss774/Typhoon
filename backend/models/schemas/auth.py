"""
Auth Schemas — register, login, user response
==============================================
Port of `backend/models/types.ts` Auth section.
"""

from __future__ import annotations

from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    email: str = Field(..., min_length=1)
    password: str = Field(..., min_length=6)
    first_name: str = Field(..., min_length=1)
    last_name: str = Field(..., min_length=1)
    role: str = "assureur"


class LoginRequest(BaseModel):
    email: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)


class UserResponse(BaseModel):
    id: str
    email: str
    first_name: str
    last_name: str
    role: str


class AuthResponse(BaseModel):
    user: UserResponse


class SupabaseLoginRequest(BaseModel):
    access_token: str = Field(..., min_length=1)


class ApiError(BaseModel):
    error: str
    message: str
