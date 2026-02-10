"""Module containing Expense Pydantic models."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any
from uuid import UUID

from dotenv import load_dotenv
from pydantic import BaseModel, Field, ValidationInfo, field_validator

from ..domain.currencies.currency import Currency
from ..domain.expenses.expense import ExpenseStatus

dotenv_loaded = load_dotenv(Path(__file__).resolve().parent.parent / "../.env")


class ExpenseCreate(BaseModel):
    account_id: UUID
    description: str
    amount: Decimal
    category_id: UUID
    expense_date: date
    currency: Currency
    status: ExpenseStatus = ExpenseStatus.COMPLETED
    global_event_id: UUID | None = None
    personal_responsibility_factor: Decimal | None = Field(None, ge=0, le=1)
    calculated_user_share: Decimal | None = (None,)

    @field_validator("description", mode="before")
    @classmethod
    def non_empty_str(cls, value: Any, info: ValidationInfo) -> str:
        if value is None:
            raise ValueError(f"{info.field_name} must not be empty.")

        try:
            s = str(value)
        except Exception as e:
            raise ValueError(f"{info.field_name} must be a string. Got type {type(value)}.") from e

        s = s.strip()
        if not s:
            raise ValueError(f"{info.field_name} must not be blank.")

        return s

    @field_validator("amount", mode="before")
    @classmethod
    def parse_amount(cls, value: Any) -> Decimal:
        if value is None:
            raise ValueError("amount is required.")

        if isinstance(value, Decimal):
            dec = value
        else:
            try:
                dec = Decimal(str(value))
            except (InvalidOperation, TypeError) as e:
                raise ValueError("amount must be a valid number.") from e

        if dec < 0:
            raise ValueError("amount must be non-negative.")

        return dec

    @field_validator("expense_date")
    @classmethod
    def not_in_future(cls, value: date) -> date:
        if value > date.today():
            raise ValueError("expense_date cannot be in the future.")
        return value


class ExpenseRead(BaseModel):
    id: UUID
    account_id: UUID
    description: str
    amount: Decimal
    category_id: UUID
    status: ExpenseStatus
    currency: Currency
    personal_responsibility_factor: Decimal | None = Field(None, ge=0, le=1)
    calculated_user_share: Decimal | None = (None,)
    expense_date: date
    created_by_user_id: UUID | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ExpenseUpdate(BaseModel):
    description: str | None = None
    amount: Decimal | None = None
    category_id: UUID | None = None
    expense_date: date | None = None
    currency: Currency | None = None
    global_event_id: UUID | None = None
    personal_responsibility_factor: Decimal | None = Field(None, ge=0, le=1)
    calculated_user_share: Decimal | None = (None,)

    @field_validator("description", mode="before")
    @classmethod
    def non_empty_str(cls, value: Any, info: ValidationInfo) -> str | None:
        if value is None:
            return None

        try:
            s = str(value)
        except Exception as e:
            raise ValueError(f"{info.field_name} must be a string. Got type {type(value)}.") from e

        s = s.strip()
        if not s:
            raise ValueError(f"{info.field_name} must not be blank.")

        return s

    @field_validator("amount", mode="before")
    @classmethod
    def parse_amount(cls, value: Any) -> Decimal | None:
        if value is None:
            return None

        if isinstance(value, Decimal):
            dec = value
        else:
            try:
                dec = Decimal(str(value))
            except (InvalidOperation, TypeError) as e:
                raise ValueError("amount must be a valid number.") from e

        if dec < 0:
            raise ValueError("amount must be non-negative.")

        return dec

    @field_validator("expense_date")
    @classmethod
    def not_in_future(cls, value: date) -> date | None:
        if value is None:
            return None

        if value > date.today():
            raise ValueError("expense_date cannot be in the future.")
        return value


class ExpenseFilterParams(BaseModel):
    # Search & Filter
    account_id: UUID
    status: ExpenseStatus | None = None
    start_date: date | None = None
    end_date: date | None = None
    category_id: UUID | None = None
    min_amount: float | None = None
    max_amount: float | None = None
    search_query: str | None = None
    user_id: UUID | None = None

    # Pagination & Offset
    limit: int = 20
    offset: int = 0


class PaginatedExpenseResponse(BaseModel):
    items: list[ExpenseRead]
    total_amount: float
    total_count: int
    limit: int
    offset: int
    total_amount_formatted: str
    rates_updated_at: datetime | None = None
    base_currency: str = "EUR"
