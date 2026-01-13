from datetime import date
from uuid import uuid4

import pytest
from httpx import AsyncClient

from app.domain.expenses.expense import ExpenseCategory


@pytest.mark.asyncio
async def test_search_unauthorized_account(client: AsyncClient, user_token_headers):
    """
    Test that a search for a random account returns 404 or 403.
    """
    random_account_id = str(uuid4())
    search_payload = {"account_id": random_account_id, "limit": 20, "offset": 0}

    response = await client.post("/api/v1/expenses/search", json=search_payload, headers=user_token_headers)

    assert response.status_code in [403, 404]


@pytest.mark.asyncio
async def test_search_pagination_logic(client: AsyncClient, user_token_headers, test_account, test_expenses):
    """
    Test that pagination works correctly for an authorized account.
    """
    search_payload = {"account_id": str(test_account.id), "limit": 1, "offset": 0}

    response = await client.post("/api/v1/expenses/search", json=search_payload, headers=user_token_headers)

    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 1
    assert data["total_count"] == 2


@pytest.mark.asyncio
async def test_search_filter_by_category_and_date(client: AsyncClient, user_token_headers, test_account, test_expenses):
    """
    Test that filtering by category and date range actually returns only matching items.
    """
    search_payload = {
        "account_id": str(test_account.id),
        "category": ExpenseCategory.BILLS.value,
        "start_date": str(date.today()),
        "end_date": str(date.today()),
        "limit": 10,
        "offset": 0,
    }

    response = await client.post("/api/v1/expenses/search", json=search_payload, headers=user_token_headers)

    assert response.status_code == 200
    data = response.json()

    assert data["total_count"] == 1
    assert data["items"][0]["category"] == ExpenseCategory.BILLS.value
    assert data["items"][0]["description"] == "Weekly Shop"
