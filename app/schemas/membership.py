"""Module containing Membership Pydantic models."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID  # noqa: TCH003

from pydantic import BaseModel

from ..domain.memberships.membership import MembershipRole  # noqa: TCH001


class MembershipCreate(BaseModel):
    user_id: UUID
    account_id: UUID
    role: MembershipRole


class MembershipRead(BaseModel):
    id: UUID
    user_id: UUID
    account_id: UUID
    role: MembershipRole
    created_at: datetime

    model_config = {"from_attributes": True}


class MembershipUpdate(BaseModel):
    role: MembershipRole | None = None
