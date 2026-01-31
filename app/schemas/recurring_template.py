"""Module containing RecurringTemplate Pydantic models."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from pydantic import BaseModel

from ..domain.currencies.currency import Currency
from ..domain.frequency_type import FrequencyType


class RecurringTemplateRead(BaseModel):
    description: str
    name: str
    amount: Decimal
    currency: Currency
    frequency: FrequencyType
    anchor_date: date
    next_occurrence_date: date
    is_active: bool
    icon: str

    model_config = {"from_attributes": True}
