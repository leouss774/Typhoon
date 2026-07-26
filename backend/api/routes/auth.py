"""
Auth Routes — Register, Login, Logout, Me, Supabase Login
==========================================================
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Response, status

from api.deps import CurrentUser, DbSession
from models.schemas.auth import AuthResponse, LoginRequest, RegisterRequest, SupabaseLoginRequest, UserResponse
from repositories.user_repo import UserRepository
from services.auth_service import AuthService

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(data: RegisterRequest, db: DbSession, response: Response):
    """Register a new user."""
    existing = UserRepository.get_by_email(db, data.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"error": "EMAIL_EXISTS", "message": "Cet email est déjà utilisé"},
        )

    password_hash = AuthService.hash_password(data.password)
    user = UserRepository.create(
        db,
        email=data.email,
        password_hash=password_hash,
        first_name=data.first_name,
        last_name=data.last_name,
        role=data.role,
    )

    token = AuthService.create_token(user.id, user.email, user.role)
    response.headers["Set-Cookie"] = AuthService.build_cookie(token)

    return AuthResponse(
        user=UserResponse(
            id=user.id,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            role=user.role,
        )
    )


@router.post("/login")
async def login(data: LoginRequest, db: DbSession, response: Response):
    """Authenticate a user."""
    user = UserRepository.get_by_email(db, data.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "INVALID_CREDENTIALS", "message": "Email ou mot de passe incorrect"},
        )

    valid = AuthService.verify_password(data.password, user.password_hash)
    if not valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "INVALID_CREDENTIALS", "message": "Email ou mot de passe incorrect"},
        )

    token = AuthService.create_token(user.id, user.email, user.role)
    response.headers["Set-Cookie"] = AuthService.build_cookie(token)

    return AuthResponse(
        user=UserResponse(
            id=user.id,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            role=user.role,
        )
    )


@router.post("/supabase-login")
async def supabase_login(data: SupabaseLoginRequest, db: DbSession, response: Response):
    """
    Exchange a Supabase Auth access token for a local session cookie.

    The frontend calls this after a user signs in via Supabase Auth
    (magic link, Google OAuth, etc.). The backend:
    1. Verifies the Supabase JWT
    2. Creates a local user record if one doesn't exist
    3. Sets an httpOnly JWT cookie for subsequent requests
    """
    access_token = data.access_token

    from core.supabase import verify_supabase_jwt

    supabase_user = verify_supabase_jwt(access_token)
    if not supabase_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "INVALID_TOKEN", "message": "Le token Supabase est invalide ou expiré"},
        )

    email = supabase_user.get("email", "")
    sub = supabase_user.get("sub", "")
    user_meta = supabase_user.get("user_metadata", {})
    first_name = user_meta.get("full_name", "") or user_meta.get("name", "") or email.split("@")[0] or "Utilisateur"
    last_name = "Supabase"

    # Find or create local user
    user = UserRepository.get_by_email(db, email)
    if not user:
        user = UserRepository.create(
            db,
            id=sub,
            email=email,
            password_hash="",  # Supabase handles auth
            first_name=first_name.split(" ")[0] if " " in first_name else first_name,
            last_name=first_name.split(" ")[-1] if " " in first_name else "",
            role="assureur",
        )

    # Set cookie
    token = AuthService.create_token(user.id, user.email, user.role)
    response.headers["Set-Cookie"] = AuthService.build_cookie(token)

    return AuthResponse(
        user=UserResponse(
            id=user.id,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            role=user.role,
        )
    )


@router.post("/logout")
async def logout(response: Response):
    """Clear the auth cookie."""
    response.headers["Set-Cookie"] = AuthService.clear_cookie()
    return {"success": True}


@router.get("/me")
async def me(current_user: CurrentUser, db: DbSession):
    """Get the current authenticated user.

    For custom JWT users: look up the user in the database.
    For Supabase Auth users: return user info from the JWT token directly.
    """
    user = UserRepository.get_by_id(db, current_user.sub)
    if user:
        return AuthResponse(
            user=UserResponse(
                id=user.id,
                email=user.email,
                first_name=user.first_name,
                last_name=user.last_name,
                role=user.role,
            )
        )
    # Supabase Auth user — return JWT data directly
    return AuthResponse(
        user=UserResponse(
            id=current_user.sub,
            email=current_user.email,
            first_name="Utilisateur",
            last_name="Supabase",
            role=current_user.role,
        )
    )
