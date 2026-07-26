"""
Database Connection — SQLAlchemy 2.0
====================================
Supports both SQLite (development) and PostgreSQL (Supabase/production).

Uses sync SQLAlchemy — FastAPI runs sync dependencies in a threadpool
with no performance penalty. External API calls use httpx (async).
"""

from __future__ import annotations

from collections.abc import Generator
from typing import Any

from sqlalchemy import Engine, create_engine, event
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from core.config import settings


def _sqlite_connect_args() -> dict[str, Any]:
    """Connection args for SQLite (single-threaded dev)."""
    return {"check_same_thread": False}


def _get_connect_args() -> dict[str, Any]:
    """Return appropriate connection args based on database type."""
    if settings.is_sqlite:
        return _sqlite_connect_args()
    return {}


def _get_engine_kwargs() -> dict[str, Any]:
    """Return engine-specific kwargs based on database type."""
    kwargs: dict[str, Any] = {"echo": False}
    if settings.is_postgres:
        # PostgreSQL pool settings (good for Supabase)
        kwargs["pool_size"] = 5
        kwargs["max_overflow"] = 10
        kwargs["pool_pre_ping"] = True
    return kwargs


class Base(DeclarativeBase):
    """Declarative base for all ORM models."""

    __allow_unmapped__ = False


engine: Engine = create_engine(
    settings.DATABASE_URL,
    connect_args=_get_connect_args(),
    **_get_engine_kwargs(),
)


@event.listens_for(engine, "connect")
def _set_sqlite_pragma(dbapi_connection: Any, _connection_record: Any) -> None:
    """Enable WAL mode and foreign keys on every SQLite connection."""
    if settings.is_sqlite:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


SessionLocal: sessionmaker[Session] = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency — yields a SQLAlchemy session and closes it
    after the request completes.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
