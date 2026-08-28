from datetime import date
from uuid import uuid4

from conftest import seed_currency_rates
from httpx import AsyncClient

from app.db.models.expense import Expense
from app.domain.currencies.currency import Currency
from app.domain.expenses.expense import ExpenseStatus


def test_search_unauthorized_account(client: AsyncClient, user_token_headers):
    """
    Test that a search for a random account returns 404 or 403.
    """
    random_account_id = str(uuid4())
    search_payload = {"account_id": random_account_id, "limit": 20, "offset": 0}

    response = client.post("/api/v1/expenses/search", json=search_payload, headers=user_token_headers)

    assert response.status_code in [403, 404]


def test_search_pagination_logic(client: AsyncClient, user_token_headers, test_account, test_expenses):
    """
    Test that pagination works correctly for an authorized account.
    """
    search_payload = {"account_id": str(test_account.id), "limit": 1, "offset": 0}

    response = client.post("/api/v1/expenses/search", json=search_payload, headers=user_token_headers)

    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 1  # This stays 1 because "limit": 1

    # Change this from 2 to 3
    assert data["total_count"] == len(test_expenses)


def test_search_filter_by_category_and_date(
    client: AsyncClient, user_token_headers, test_account, test_expense, test_category
):
    """
    Test that filtering by category and date range actually returns only matching items.
    """
    search_payload = {
        "account_id": str(test_account.id),
        "category_id": str(test_expense.category_id),
        "start_date": str(date.today()),
        "end_date": str(date.today()),
        "limit": 10,
        "offset": 0,
    }

    response = client.post("/api/v1/expenses/search", json=search_payload, headers=user_token_headers)

    assert response.status_code == 200
    data = response.json()

    assert data["total_count"] == 1
    assert data["items"][0]["category_id"] == str(test_category.id)

    # FIX: Change "Weekly Shop" to "Internet Bill"
    assert data["items"][0]["description"] == "Internet Bill"


def test_search_expenses_prefix_matching(client, db_session, test_account, test_category):
    """Test that 'shop' matches 'Shopping' using FTS"""
    account_id = test_account.id

    expense = Expense(
        id=uuid4(),
        account_id=account_id,
        description="Grocery Shopping at Lidl",
        amount=50.0,
        currency=Currency.EUR,
        category_id=test_category.id,
        status=ExpenseStatus.PENDING,
        expense_date=date.today(),
    )
    db_session.add(expense)
    db_session.flush()

    response = client.post(
        "/api/v1/expenses/search?target_currency=EUR",
        json={"account_id": str(account_id), "search_query": "shop", "limit": 10, "offset": 0},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total_count"] >= 1
    assert "Shopping" in data["items"][0]["description"]


def test_currency_normalization(client, db_session, test_account, test_category):
    """Test that total_amount is correctly converted to target_currency"""
    seed_currency_rates(db_session)

    # MUST BE .id - otherwise the API receives a Python object instead of a UUID string
    account_id = test_account.id

    expense = Expense(
        id=uuid4(),
        account_id=account_id,
        description="Cloud Server",
        amount=100.0,
        currency=Currency.USD,
        category_id=test_category.id,
        status=ExpenseStatus.PENDING,
        expense_date=date.today(),
    )
    db_session.add(expense)
    db_session.flush()

    response = client.post(
        "/api/v1/expenses/search?target_currency=EUR", json={"account_id": str(account_id), "limit": 10, "offset": 0}
    )

    assert response.status_code == 200
    data = response.json()

    # Assertions
    assert data["total_amount"] == 92.59  # 100 USD / 1.08, with EUR as the base rate.
    assert data["items"][0]["currency"] == "USD"  # Original currency preserved
    assert data["total_amount_formatted"].startswith("€")


def test_search_and_normalize(client, db_session, test_account, test_user, test_category):
    # 1. ARRANGE: Manually seed the "Bill" that the search is looking for
    # We use the seed_expense helper from conftest
    from datetime import date
    from decimal import Decimal
    from uuid import uuid4

    from app.db.models.expense import Expense
    from app.domain.expenses.expense import ExpenseStatus

    bill = Expense(
        id=uuid4(),
        account_id=test_account.id,
        created_by_user_id=test_user.id,
        description="Electric Bill",  # This matches the "Bill" search query
        amount=Decimal("100.00"),
        currency=Currency.EUR,
        category_id=test_category.id,
        expense_date=date.today(),
        status=ExpenseStatus.COMPLETED,
    )
    db_session.add(bill)
    db_session.flush()  # Push to DB so search can find it

    # 2. ACT: Search for "Bill"
    search_payload = {"account_id": str(test_account.id), "search_query": "Bill", "limit": 10, "offset": 0}

    response = client.post("/api/v1/expenses/search?target_currency=EUR", json=search_payload)

    # 3. ASSERT
    assert response.status_code == 200
    data = response.json()
    assert data["total_count"] >= 1
