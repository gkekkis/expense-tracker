"""
Orchestration service for setting up new user accounts.
Handles initial data seeding, such as default recurring templates
to provide a 'ready-to-use' experience for new users.
"""

from __future__ import annotations

import datetime

from sqlalchemy.orm import Session

from ...db.models.account import Account
from ...db.models.recurring_template import RecurringTemplate
from ...domain.currencies.currency import Currency
from ...domain.expenses.expense import ExpenseCategory
from ...domain.frequency_type import FrequencyType


def process_new_account_onboarding(
    session: Session, account: Account, category_map: dict[ExpenseCategory, str]
) -> Account:
    """
    Seeds initial data for a newly created account.
    Creates a 'Welcome' Netflix template to demonstrate recurring logic.
    """
    # Define the 'Tutorial' Netflix template
    recurring_template = RecurringTemplate(
        account_id=account.id,
        category_id=category_map[ExpenseCategory.ENTERTAINMENT],
        name="Netflix",
        amount=15.99,
        currency=Currency.EUR,
        # We use today for both to trigger an immediate 'due' state
        anchor_date=datetime.date.today(),
        next_occurrence_date=datetime.date.today(),
        icon="🍿",
        frequency=FrequencyType.MONTHLY,
        is_active=True,
    )

    session.add(recurring_template)

    # Return the account object to match the signature and allow chaining
    return account
