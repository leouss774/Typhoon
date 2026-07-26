"""
User Repository — database access for User model.
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from models.db import User


class UserRepository:
    """CRUD operations for the User model."""

    @staticmethod
    def get_by_id(db: Session, user_id: str) -> User | None:
        return db.get(User, user_id)

    @staticmethod
    def get_by_email(db: Session, email: str) -> User | None:
        return db.execute(select(User).where(User.email == email)).scalar_one_or_none()

    @staticmethod
    def create(db: Session, **kwargs) -> User:
        user = User(**kwargs)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def list_all(db: Session) -> list[User]:
        return list(db.execute(select(User)).scalars().all())
