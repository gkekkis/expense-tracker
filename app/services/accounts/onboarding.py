"""Helpers for seeding useful default data when a new account is created."""

from __future__ import annotations

import datetime
from uuid import UUID

from sqlalchemy.orm import Session

from ...db.models.account import Account
from ...db.models.recurring_template import RecurringTemplate
from ...domain.currencies.currency import Currency
from ...domain.expenses.expense import ExpenseCategory
from ...domain.frequency_type import FrequencyType


def process_new_account_onboarding(
    session: Session, account: Account, category_ids: dict[ExpenseCategory, UUID]
) -> Account:
    """Seed a small recurring-template example for a new account."""
    recurring_template = RecurringTemplate(
        account_id=account.id,
        category_id=category_ids[ExpenseCategory.ENTERTAINMENT],
        description="Netflix subscription",
        name="Netflix",
        amount=15.99,
        currency=Currency.EUR,
        anchor_date=datetime.date.today(),
        next_occurrence_date=datetime.date.today(),
        icon="N",
        frequency=FrequencyType.MONTHLY,
        is_active=True,
    )

    session.add(recurring_template)
    return account
