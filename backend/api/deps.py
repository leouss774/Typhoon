"""
FastAPI Dependencies
====================
Shared dependencies used across route modules.
"""

from __future__ import annotations

from typing import Annotated, Generator

from fastapi import Depends
from sqlalchemy.orm import Session

from core.database import get_db
from core.user_context import UserContext

# Re-export for convenience
from api.middleware.auth import optional_auth, require_auth

DbSession = Annotated[Session, Depends(get_db)]
CurrentUser = Annotated[UserContext, Depends(require_auth)]
OptionalUser = Annotated[UserContext | None, Depends(optional_auth)]
