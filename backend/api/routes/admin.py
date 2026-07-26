"""
Admin Routes
============
Administrative endpoints for platform oversight:
- User management (list, create, toggle status)
- Platform statistics
- System audit (all assessments)

All routes require admin role.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from api.deps import CurrentUser, DbSession
from core.database import get_db
from core.user_context import UserContext
from models.db.user import User
from models.db.assessment import Assessment
from models.db.client import Client
from models.db.property import Property
from pydantic import BaseModel, EmailStr

router = APIRouter(prefix="/api/admin", tags=["admin"])


def require_admin(current_user: CurrentUser) -> None:
    """Check that the current user has admin role."""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")


# ─── Schemas ────────────────────────────────────────────────────


class AdminStats(BaseModel):
    total_users: int
    total_assureurs: int
    total_assures: int
    total_clients: int
    total_properties: int
    total_assessments: int
    assessments_this_month: int


class UserResponse(BaseModel):
    id: str
    email: str
    role: str
    first_name: str
    last_name: str


class CreateUserRequest(BaseModel):
    email: str
    password: str
    first_name: str
    last_name: str
    role: str = "assureur"


# ─── Routes ─────────────────────────────────────────────────────


@router.get("/stats", response_model=AdminStats)
async def get_admin_stats(
    current_user: CurrentUser,
    db: DbSession,
):
    """Platform-wide statistics."""
    require_admin(current_user)

    total_users = db.query(func.count(User.id)).scalar() or 0
    total_assureurs = db.query(func.count(User.id)).filter(User.role == "assureur").scalar() or 0
    total_assures = db.query(func.count(User.id)).filter(User.role == "assure").scalar() or 0
    total_clients = db.query(func.count(Client.id)).scalar() or 0
    total_properties = db.query(func.count(Property.id)).scalar() or 0
    total_assessments = db.query(func.count(Assessment.id)).scalar() or 0

    from datetime import datetime, timezone
    from sqlalchemy import extract

    now = datetime.now(timezone.utc)
    assessments_this_month = (
        db.query(func.count(Assessment.id))
        .filter(
            extract("year", Assessment.created_at) == now.year,
            extract("month", Assessment.created_at) == now.month,
        )
        .scalar()
        or 0
    )

    return AdminStats(
        total_users=total_users,
        total_assureurs=total_assureurs,
        total_assures=total_assures,
        total_clients=total_clients,
        total_properties=total_properties,
        total_assessments=total_assessments,
        assessments_this_month=assessments_this_month,
    )


@router.get("/users", response_model=list[UserResponse])
async def list_all_users(
    current_user: CurrentUser,
    db: DbSession,
):
    """List all platform users."""
    require_admin(current_user)

    users = db.query(User).order_by(User.created_at.desc()).all()
    return [
        UserResponse(
            id=u.id,
            email=u.email,
            role=u.role,
            first_name=u.first_name,
            last_name=u.last_name,
        )
        for u in users
    ]


@router.post("/users", response_model=UserResponse)
async def create_user(
    data: CreateUserRequest,
    current_user: CurrentUser,
    db: DbSession,
):
    """Create a new user (admin only)."""
    require_admin(current_user)

    from core.security import hash_password

    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        raise HTTPException(status_code=409, detail="Email already exists")

    user = User(
        email=data.email,
        password_hash=hash_password(data.password),
        role=data.role,
        first_name=data.first_name,
        last_name=data.last_name,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return UserResponse(
        id=user.id,
        email=user.email,
        role=user.role,
        first_name=user.first_name,
        last_name=user.last_name,
    )


@router.get("/assessments")
async def list_all_assessments(
    current_user: CurrentUser,
    db: DbSession,
):
    """List all assessments across the platform."""
    require_admin(current_user)

    assessments = (
        db.query(Assessment)
        .order_by(Assessment.created_at.desc())
        .limit(100)
        .all()
    )
    return [
        {
            "id": a.id,
            "address_label": a.address_label,
            "status": a.status,
            "global_score": a.global_score,
            "created_at": a.created_at.isoformat() if a.created_at else None,
        }
        for a in assessments
    ]
