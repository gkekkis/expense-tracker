"""Module containing RecurringTemplate Pydantic models."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field

from ..domain.currencies.currency import Currency
from ..domain.frequency_type import FrequencyType


class RecurringTemplateCreate(BaseModel):
    account_id: UUID
    category_id: UUID
    description: str
    name: str
    amount: Decimal
    currency: Currency = Currency.EUR
    frequency: FrequencyType = FrequencyType.MONTHLY
    anchor_date: date
    icon: str
    is_active: bool = True
    # NEW: Responsibility Logic
    global_event_id: UUID | None = None
    personal_responsibility_factor: Decimal | None = Field(None, ge=0, le=1)


class RecurringTemplateUpdate(BaseModel):
    # PATCH model
    category_id: UUID | None = None
    description: str | None = None
    name: str | None = None
    amount: Decimal | None = None
    currency: Currency | None = None
    frequency: FrequencyType | None = None
    anchor_date: date | None = None
    icon: str | None = None
    is_active: bool | None = None
    global_event_id: UUID | None = None
    personal_responsibility_factor: Decimal | None = Field(None, ge=0, le=1)


class RecurringTemplateRead(BaseModel):
    id: UUID
    account_id: UUID
    category_id: UUID
    created_by_user_id: UUID | None = None

    description: str
    name: str
    amount: Decimal
    currency: Currency
    frequency: FrequencyType
    anchor_date: date
    next_occurrence_date: date
    is_active: bool
    icon: str

    global_event_id: UUID | None = None
    personal_responsibility_factor: Decimal | None = None

    model_config = {"from_attributes": True}
