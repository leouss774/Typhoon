"""Data access repositories — thin wrappers around SQLAlchemy CRUD."""

from repositories.user_repo import UserRepository
from repositories.client_repo import ClientRepository
from repositories.property_repo import PropertyRepository
from repositories.assessment_repo import AssessmentRepository

__all__ = [
    "UserRepository",
    "ClientRepository",
    "PropertyRepository",
    "AssessmentRepository",
]
