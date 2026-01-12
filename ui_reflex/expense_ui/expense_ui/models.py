from __future__ import annotations

from typing import Literal

from pydantic import BaseModel


class Account(BaseModel):
    id: str
    name: str
    status: Literal["ACTIVE", "INACTIVE"]
    created_at: str
    updated_at: str


class Expense(BaseModel):
    id: str
    account_id: str
    description: str
    amount: str  # your backend returns Decimal as string in ExpenseRead
    category: str
    expense_date: str
    created_by_user_id: str | None
    created_at: str
    updated_at: str
