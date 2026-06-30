"""Module containing Membership Pydantic models."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import UUID  # noqa: TCH003

from pydantic import BaseModel, Field

from ..domain.memberships.membership import MembershipRole  # noqa: TCH001


class MembershipBase(BaseModel):
    user_id: UUID
    account_id: UUID
    role: MembershipRole
    default_contribution_share: Decimal = Field(default=Decimal("1.00"), ge=0, le=1)


class MembershipCreate(BaseModel):
    user_id: UUID
    account_id: UUID
    role: MembershipRole
    default_contribution_share: Decimal = Field(default=Decimal("1.00"), ge=0, le=1)


class MembershipRead(BaseModel):
    id: UUID
    user_id: UUID
    account_id: UUID
    role: MembershipRole
    default_contribution_share: Decimal = Field(default=Decimal("1.00"), ge=0, le=1)
    created_at: datetime

    model_config = {"from_attributes": True}


class MembershipUpdate(BaseModel):
    role: MembershipRole | None = None
    default_contribution_share: Decimal | None = Field(None, ge=0, le=1)
