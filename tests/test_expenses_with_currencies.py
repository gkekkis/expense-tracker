import pytest


@pytest.mark.asyncio
async def test_search_and_normalize(client, test_account, test_expenses, seed_currency_rates):
    # 1. Search for "Rent"
    search_payload = {"account_id": str(test_account.id), "search_query": "Rent", "limit": 10, "offset": 0}

    response = await client.post("/api/v1/expenses/search?target_currency=EUR", json=search_payload)

    assert response.status_code == 200
    data = response.json()

    # 2. Verify results
    assert data["total_count"] == 1
    assert "Rent" in data["items"][0]["description"]

    # 3. Verify Currency Conversion
    # Now that seed_currency_rates is active, 1200 USD / 1.08 = 1111.11 EUR
    assert data["total_amount"] < 1200.0
