"""
Test Fixtures
=============
Provides a FastAPI test client with an isolated SQLite in-memory database.

NOTE: SQLite `:memory:` creates a fresh DB per connection, so we use
a temporary file-based database to share the schema across sessions.
"""

from __future__ import annotations

import os
import tempfile
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

# Import all models so they register on Base.metadata
import models.db  # noqa: F401
from api.main import app
from core.database import Base, get_db

# ─── Temporary file-based SQLite database for tests ──────────────
_db_fd, _db_path = tempfile.mkstemp(suffix=".test.db")

TEST_ENGINE = create_engine(
    f"sqlite:///{_db_path}",
    connect_args={"check_same_thread": False},
)
TEST_SESSION_LOCAL = sessionmaker(autocommit=False, autoflush=False, bind=TEST_ENGINE)


def override_get_db() -> Generator[Session, None, None]:
    """Yield a test DB session (tables already exist)."""
    db = TEST_SESSION_LOCAL()
    try:
        yield db
    finally:
        db.close()


# Create all tables once at import time on the shared engine
Base.metadata.create_all(bind=TEST_ENGINE)


@pytest.fixture(autouse=True)
def clean_db() -> Generator[None, None, None]:
    """Clear all data between tests (keep schema)."""
    with TEST_ENGINE.connect() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            conn.execute(table.delete())
        conn.commit()
    yield


@pytest.fixture()
def db() -> Generator[Session, None, None]:
    yield from override_get_db()


@pytest.fixture()
def client() -> Generator[TestClient, None, None]:
    """FastAPI test client with overridden DB dependency."""
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def pytest_unconfigure() -> None:
    """Clean up the temporary database file."""
    try:
        os.close(_db_fd)
        os.unlink(_db_path)
    except OSError:
        pass
