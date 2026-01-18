from datetime import date
from uuid import uuid4

import pytest

from app.db.models.expense import Expense
from app.domain.currencies.currency import Currency
from app.domain.expenses.expense import ExpenseCategory


@pytest.mark.asyncio
async def test_search_expenses_prefix_matching(client, db_session, test_account):
    """Test that 'shop' matches 'Shopping' using FTS"""
    account_id = test_account.id

    expense = Expense(
        id=uuid4(),
        account_id=account_id,
        description="Grocery Shopping at Lidl",
        amount=50.0,
        currency=Currency.EUR,
        category=ExpenseCategory.GROCERIES,
        expense_date=date.today(),
    )
    db_session.add(expense)
    db_session.flush()

    response = await client.post(
        "/api/v1/expenses/search?target_currency=EUR",
        json={"account_id": str(account_id), "search_query": "shop", "limit": 10, "offset": 0},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total_count"] >= 1
    assert "Shopping" in data["items"][0]["description"]


@pytest.mark.asyncio
async def test_currency_normalization(client, db_session, test_account):
    """Test that total_amount is correctly converted to target_currency"""
    # MUST BE .id - otherwise the API receives a Python object instead of a UUID string
    account_id = test_account.id

    expense = Expense(
        id=uuid4(),
        account_id=account_id,
        description="Cloud Server",
        amount=100.0,
        currency=Currency.USD,
        category=ExpenseCategory.BILLS,
        expense_date=date.today(),
    )
    db_session.add(expense)
    db_session.flush()

    response = await client.post(
        "/api/v1/expenses/search?target_currency=EUR", json={"account_id": str(account_id), "limit": 10, "offset": 0}
    )

    assert response.status_code == 200
    data = response.json()

    # Assertions
    assert data["total_amount"] != 100.0  # Should be converted to EUR
    assert data["items"][0]["currency"] == "USD"  # Original currency preserved
    assert data["total_amount_formatted"].startswith("€")
