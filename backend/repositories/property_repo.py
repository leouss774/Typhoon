"""
Property Repository — database access for Property model.
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from models.db import Property


class PropertyRepository:
    """CRUD operations for the Property model."""

    @staticmethod
    def get_by_id(db: Session, property_id: str) -> Property | None:
        return db.get(Property, property_id)

    @staticmethod
    def get_by_client_id(db: Session, client_id: str) -> Property | None:
        return db.execute(
            select(Property).where(Property.client_id == client_id)
        ).scalar_one_or_none()

    @staticmethod
    def list_all(db: Session) -> list[Property]:
        return list(db.execute(select(Property)).scalars().all())

    @staticmethod
    def create(db: Session, **kwargs) -> Property:
        prop = Property(**kwargs)
        db.add(prop)
        db.commit()
        db.refresh(prop)
        return prop

    @staticmethod
    def update(db: Session, prop: Property, **kwargs) -> Property:
        for key, value in kwargs.items():
            setattr(prop, key, value)
        db.commit()
        db.refresh(prop)
        return prop

    @staticmethod
    def delete(db: Session, prop: Property) -> None:
        db.delete(prop)
        db.commit()
