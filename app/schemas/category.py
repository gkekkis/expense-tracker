"""Module containing Category Pydantic models."""

from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel


class CategoryRead(BaseModel):
    id: UUID
    account_id: UUID
    name: str
    emoji: str

    model_config = {"from_attributes": True}
