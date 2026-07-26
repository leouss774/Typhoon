"""
Client Repository — database access for Client model.
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from models.db import Client, Property


class ClientRepository:
    """CRUD operations for the Client model."""

    @staticmethod
    def get_by_id(db: Session, client_id: str) -> Client | None:
        return db.get(Client, client_id)

    @staticmethod
    def get_by_id_and_user(db: Session, client_id: str, user_id: str) -> Client | None:
        return db.execute(
            select(Client).where(Client.id == client_id, Client.user_id == user_id)
        ).scalar_one_or_none()

    @staticmethod
    def list_by_user(db: Session, user_id: str) -> list[Client]:
        return list(
            db.execute(
                select(Client).where(Client.user_id == user_id)
            ).scalars().all()
        )

    @staticmethod
    def create(db: Session, **kwargs) -> Client:
        client = Client(**kwargs)
        db.add(client)
        db.commit()
        db.refresh(client)
        return client

    @staticmethod
    def update(db: Session, client: Client, **kwargs) -> Client:
        for key, value in kwargs.items():
            if value is not None:
                setattr(client, key, value)
        db.commit()
        db.refresh(client)
        return client

    @staticmethod
    def delete(db: Session, client: Client) -> None:
        db.delete(client)
        db.commit()

    @staticmethod
    def get_properties(db: Session, client_id: str) -> list[Property]:
        return list(
            db.execute(
                select(Property).where(Property.client_id == client_id)
            ).scalars().all()
        )
