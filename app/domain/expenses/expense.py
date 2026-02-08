"""Blueprint module of the Expense domain class."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from enum import Enum
from uuid import UUID, uuid4

from ..currencies.currency import Currency


class ExpenseCategory(Enum):
    """Blueprint class containing expense categories."""

    RENTAL = "Rental"
    BILLS = "Bills"
    GROCERIES = "Groceries"
    HOUSEHOLD = "Household"
    DELIVERY_FOOD = "Delivery Food"
    DINING_OUT = "Dining Out"
    PET = "Pet"
    GAS = "Gas"
    CAR = "Car"
    TRAVEL = "Travel"
    ENTERTAINMENT = "Entertainment"
    HEALTH = "Health"
    PERSONAL = "Personal"
    SAVINGS = "Savings"
    MISC = "Miscellaneous"


class ExpenseStatus(Enum):
    """Blueprint class containing expense status."""

    PENDING = "Pending"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"


class Expense:
    """Expense domain class."""

    def __init__(
        self,
        account_id: UUID,
        description: str,
        amount: Decimal,
        category_id: UUID,
        status: ExpenseStatus,
        expense_date: date,
        expense_id: UUID | None = None,
        currency: Currency = Currency.EUR,
        global_event_id: UUID | None = None,
        personal_responsibility_factor: Decimal | None = None,
    ) -> None:
        if not description or not str(description).strip():
            raise ValueError("description must not be empty or blank.")

        # Validation for responsibility factor (must be 0.0 to 1.0 if provided)
        if personal_responsibility_factor is not None and not (0 <= personal_responsibility_factor <= 1):
            raise ValueError("personal_responsibility_factor must be between 0 and 1.")

        self.id: UUID = expense_id or uuid4()
        self.account_id: UUID = account_id
        self.description: str = str(description).strip()
        self.amount: Decimal = amount
        self.category_id: UUID = category_id
        self.status: ExpenseStatus = status
        self.expense_date: date = expense_date
        self.currency = currency
        self.global_event_id = global_event_id
        self.personal_responsibility_factor = personal_responsibility_factor

    def __repr__(self) -> str:
        return (
            f"<id: {self.id}, account_id: {self.account_id}, "
            f"description: {self.description}, amount: {self.amount}, "
            f"category: {self.category}, expense_date: {self.expense_date}>, "
            f"currency: {self.currency}"
        )
