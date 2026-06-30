from datetime import date
from uuid import uuid4

from freezegun import freeze_time
from sqlalchemy import select

from app.db.models.expense import Expense
from app.db.models.recurring_template import RecurringTemplate
from app.domain.frequency_type import FrequencyType
from app.services.expense_service import process_recurring_templates


def test_process_recurring_templates_creates_expenses(db_session, test_account, test_category):
    # 1. ARRANGE
    template = RecurringTemplate(
        id=uuid4(),
        account_id=test_account.id,
        category_id=test_category.id,
        description="Netflix Subscription",
        name="Netflix",
        amount=15.99,
        frequency=FrequencyType.MONTHLY,
        anchor_date=date(2026, 1, 1),
        next_occurrence_date=date(2026, 1, 1),
        is_active=True,
        icon="N",
    )
    db_session.add(template)
    db_session.flush()

    # 2. ACT
    with freeze_time("2026-03-02"):
        print(f"DEBUG: Inside freeze_time, date is {date.today()}")
        process_recurring_templates(db_session)
        db_session.flush()

    # 3. ASSERT
    # Use a fresh query to see what happened
    all_expenses = db_session.execute(select(Expense)).scalars().all()
    print(f"DEBUG: Total expenses in DB: {len(all_expenses)}")
    for exp in all_expenses:
        print(f"DEBUG: Expense: {exp.description} | Date: {exp.expense_date} | Account: {exp.account_id}")

    # Now run your filtered assertion
    expenses = db_session.execute(select(Expense).where(Expense.account_id == test_account.id)).scalars().all()

    assert len(expenses) == 3
    assert expenses[0].expense_date == date(2026, 1, 1)
    assert expenses[1].expense_date == date(2026, 2, 1)
    assert expenses[2].expense_date == date(2026, 3, 1)

    db_session.refresh(template)
    assert template.next_occurrence_date == date(2026, 4, 1)
