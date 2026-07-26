"""
Client Routes — CRUD for clients
=================================
Direct port of `backend/api/routes/clients.routes.ts`.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, status
from sqlalchemy.orm import Session

from api.deps import CurrentUser, DbSession
from models.schemas.client import ClientCreate, ClientResponse, ClientUpdate
from models.schemas.property import PropertyResponse
from repositories.client_repo import ClientRepository
from repositories.property_repo import PropertyRepository

router = APIRouter(prefix="/api/clients", tags=["clients"])


@router.get("/")
async def list_clients(db: DbSession, current_user: CurrentUser):
    """List all clients for the current user."""
    clients = ClientRepository.list_by_user(db, current_user.sub)
    return [ClientResponse.model_validate(c) for c in clients]


@router.get("/{client_id}")
async def get_client(client_id: str, db: DbSession, current_user: CurrentUser):
    """Get a single client with its properties."""
    client = ClientRepository.get_by_id_and_user(db, client_id, current_user.sub)
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "NOT_FOUND", "message": "Client non trouvé"},
        )
    props = ClientRepository.get_properties(db, client_id)
    return {
        **ClientResponse.model_validate(client).model_dump(),
        "properties": [PropertyResponse.model_validate(p).model_dump() for p in props],
    }


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_client(data: ClientCreate, db: DbSession, current_user: CurrentUser):
    """Create a new client."""
    client = ClientRepository.create(
        db,
        user_id=current_user.sub,
        civility=data.civility,
        first_name=data.first_name,
        last_name=data.last_name,
        email=data.email,
        phone=data.phone,
        insured_address=data.insured_address,
        insured_postal_code=data.insured_postal_code,
        insured_city=data.insured_city,
    )
    return ClientResponse.model_validate(client)


@router.put("/{client_id}")
async def update_client(client_id: str, data: ClientUpdate, db: DbSession, current_user: CurrentUser):
    """Update a client."""
    client = ClientRepository.get_by_id_and_user(db, client_id, current_user.sub)
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "NOT_FOUND", "message": "Client non trouvé"},
        )

    update_kwargs = data.model_dump(exclude_none=True)
    updated = ClientRepository.update(db, client, **update_kwargs)
    return ClientResponse.model_validate(updated)


@router.delete("/{client_id}")
async def delete_client(client_id: str, db: DbSession, current_user: CurrentUser):
    """Delete a client."""
    client = ClientRepository.get_by_id_and_user(db, client_id, current_user.sub)
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "NOT_FOUND", "message": "Client non trouvé"},
        )
    ClientRepository.delete(db, client)
    return {"success": True}
