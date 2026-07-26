"""
Client Schemas
==============
Port of `backend/models/types.ts` Client section.
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class ClientCreate(BaseModel):
    civility: str | None = None
    first_name: str = Field(..., min_length=1)
    last_name: str = Field(..., min_length=1)
    email: str | None = None
    phone: str | None = None
    insured_address: str | None = None
    insured_postal_code: str | None = None
    insured_city: str | None = None


class ClientUpdate(BaseModel):
    civility: str | None = None
    first_name: str | None = Field(None, min_length=1)
    last_name: str | None = Field(None, min_length=1)
    email: str | None = None
    phone: str | None = None
    insured_address: str | None = None
    insured_postal_code: str | None = None
    insured_city: str | None = None
    status: str | None = None


class ClientResponse(BaseModel):
    id: str
    user_id: str
    civility: str | None
    first_name: str
    last_name: str
    email: str | None
    phone: str | None
    insured_address: str | None
    insured_postal_code: str | None
    insured_city: str | None
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ClientWithProperties(ClientResponse):
    properties: list[dict] = []
