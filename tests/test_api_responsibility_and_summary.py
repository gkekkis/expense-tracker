from decimal import Decimal
from uuid import uuid4

from conftest import seed_category


def test_fallback_to_membership_share(client, db_session, test_user, joint_account):
    """Verify that if no factor is sent, the 70% membership share is used."""
    joint_category = seed_category(db=db_session, account_id=joint_account.id, name="Joint", emoji="J")
    payload = {
        "account_id": str(joint_account.id),
        "description": "Shared Internet",
        "amount": 100.00,
        "category_id": str(joint_category.id),
        "expense_date": "2024-02-10",
        "currency": "EUR",
    }

    # We don't send personal_responsibility_factor
    response = client.post("/api/v1/expenses/", json=payload)

    assert response.status_code == 200
    data = response.json()
    # 70% of 100.00 = 70.00
    assert Decimal(str(data["calculated_user_share"])) == Decimal("70.00")


def test_global_id_deduplication_in_summary(
    client, db_session, user_token_headers, test_user, joint_account, personal_account
):
    global_id = str(uuid4())
    joint_category = seed_category(db=db_session, account_id=joint_account.id, name="Joint", emoji="J")
    personal_category = seed_category(db=db_session, account_id=personal_account.id, name="Personal", emoji="P")

    # 1. Create in Joint
    client.post(
        "/api/v1/expenses",
        json={
            "account_id": str(joint_account.id),
            "description": "Rent",
            "amount": 100.00,
            "global_event_id": global_id,
            "category_id": str(joint_category.id),
            "expense_date": "2024-02-10",  # Added
            "currency": "EUR",  # Added
        },
        headers=user_token_headers,
    )

    # 2. Create 'Mirror' in Personal
    client.post(
        "/api/v1/expenses",
        json={
            "account_id": str(personal_account.id),
            "description": "Rent Mirror",
            "amount": 100.00,
            "global_event_id": global_id,
            "category_id": str(personal_category.id),
            "expense_date": "2024-02-10",  # Added
            "currency": "EUR",  # Added
        },
        headers=user_token_headers,
    )

    # 3. Check Budget Status
    # Now that account_id is optional in the schema, this call will succeed
    response = client.get(
        "/api/v1/summaries/budget-status", params={"account_id": str(joint_account.id)}, headers=user_token_headers
    )

    assert response.status_code == 200, f"Error: {response.json()}"

    data = response.json()
    assert "total_spent" in data
    # The deduplication logic should ensure the total is 100 or 70, not 170.
    assert Decimal(str(data["total_spent"])) < Decimal("170.00")


def test_manual_factor_override(client, db_session, user_token_headers, joint_account):
    """Verify that a manual factor (e.g. 1.0) overrides the membership default (0.7)."""
    joint_category = seed_category(db=db_session, account_id=joint_account.id, name="Joint", emoji="J")
    payload = {
        "account_id": str(joint_account.id),
        "description": "I pay all of this one",
        "amount": 100.00,
        "category_id": str(joint_category.id),
        "expense_date": "2024-02-10",
        "currency": "EUR",
        "personal_responsibility_factor": 1.0,  # Overriding the 0.7 membership default
    }

    response = client.post("/api/v1/expenses", json=payload, headers=user_token_headers)

    assert response.status_code == 200
    data = response.json()
    # Should be 100.00, NOT 70.00
    assert Decimal(str(data["calculated_user_share"])) == Decimal("100.00")


def test_summary_account_isolation(client, db_session, user_token_headers, joint_account, personal_account):
    """Verify summary only counts expenses for the mandatory account_id provided."""
    joint_category = seed_category(db=db_session, account_id=joint_account.id, name="Joint", emoji="J")
    personal_category = seed_category(db=db_session, account_id=personal_account.id, name="Personal", emoji="P")

    # 1. Create $50 in Joint Account
    client.post(
        "/api/v1/expenses",
        json={
            "account_id": str(joint_account.id),
            "description": "Joint Expense",
            "amount": 50.00,
            "category_id": str(joint_category.id),
            "expense_date": "2024-02-10",
            "currency": "EUR",
        },
        headers=user_token_headers,
    )

    # 2. Create $100 in Personal Account
    client.post(
        "/api/v1/expenses",
        json={
            "account_id": str(personal_account.id),
            "description": "Personal Expense",
            "amount": 100.00,
            "category_id": str(personal_category.id),
            "expense_date": "2024-02-10",
            "currency": "EUR",
        },
        headers=user_token_headers,
    )

    # 3. Get summary SPECIFICALLY for Joint Account
    # Joint share is 0.7 * 50 = 35.00
    response = client.get(
        "/api/v1/summaries/budget-status", headers=user_token_headers, params={"account_id": str(joint_account.id)}
    )

    data = response.json()
    # It should ONLY be 35.00, completely ignoring the 100.00 in the other account
    assert Decimal(str(data["total_spent"])) == Decimal("35.00")


def test_create_expense_unauthorized_account(client, user_token_headers, test_category):
    """Verify user cannot create expenses in an account they don't belong to."""
    random_uuid = str(uuid4())
    payload = {
        "account_id": random_uuid,
        "description": "Hack",
        "amount": 10.00,
        "category_id": str(test_category.id),
        "expense_date": "2024-02-10",
        "currency": "EUR",
    }

    response = client.post("/api/v1/expenses", json=payload, headers=user_token_headers)

    # Should fail because the account doesn't exist or user isn't a member
    assert response.status_code in [403, 404]


def test_summary_zero_state(client, user_token_headers, personal_account):
    """Verify summary handles accounts with no data gracefully."""
    # 1. Get summary for a brand new, empty account
    response = client.get(
        "/api/v1/summaries/budget-status", headers=user_token_headers, params={"account_id": str(personal_account.id)}
    )

    assert response.status_code == 200
    data = response.json()

    # 2. Check that all numerical values are zero, not null/None
    assert Decimal(str(data["total_spent"])) == Decimal("0.00")
    assert Decimal(str(data["total_income"])) == Decimal("0.00")
    assert Decimal(str(data["remaining_budget"])) == Decimal("0.00")
    assert data["health_percentage"] == 0.0
