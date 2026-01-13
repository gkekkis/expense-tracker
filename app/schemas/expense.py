"""Module containing Expense Pydantic models."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ValidationInfo, field_validator

from ..domain.expenses.expense import ExpenseCategory


class ExpenseCreate(BaseModel):
    account_id: UUID
    description: str
    amount: Decimal
    category: ExpenseCategory
    expense_date: date

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
    category: ExpenseCategory
    expense_date: date
    created_by_user_id: UUID | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ExpenseUpdate(BaseModel):
    description: str | None = None
    amount: Decimal | None = None
    category: ExpenseCategory | None = None
    expense_date: date | None = None

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
    account_id: str
    start_date: date | None = None
    end_date: date | None = None
    category: ExpenseCategory | None = None
    min_amount: float | None = None
    max_amount: float | None = None
    search_query: str | None = None
    user_id: str | None = None

    # Pagination & Offset
    limit: int = 20
    offset: int = 0


class PaginatedExpenseResponse(BaseModel):
    items: list[ExpenseRead]
    total_amount: float
    total_count: int
    limit: int
    offset: int
