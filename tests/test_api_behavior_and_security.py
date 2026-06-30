import os
from uuid import UUID

from conftest import assert_http, seed_account, seed_category, seed_expense, seed_membership, seed_user
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.models.expense import ExpenseStatus
from app.db.models.financial_profile import FinancialProfile
from app.db.models.membership import MembershipRole
from app.domain.accounts.account import AccountStatus

# ---- Import your FastAPI app and DB base/models ----
# Adjust imports to match your project layout

# ---------- Test DB setup ----------
DATABASE_URL = os.getenv("PYTEST_DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("Set TEST_DATABASE_URL (preferred) or DATABASE_URL for tests.")

engine = create_engine(DATABASE_URL)
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def _seed_viewer_expense_context(db_session, *, viewer_is_creator: bool = False):
    owner = seed_user(db_session)
    viewer = seed_user(db_session)
    account = seed_account(db_session, status=AccountStatus.ACTIVE)
    seed_membership(db_session, user_id=owner.id, account_id=account.id, role=MembershipRole.OWNER)
    seed_membership(db_session, user_id=viewer.id, account_id=account.id, role=MembershipRole.VIEWER)
    category = seed_category(db=db_session, account_id=account.id, name="General", emoji="G")
    creator_id = viewer.id if viewer_is_creator else owner.id
    expense = seed_expense(db_session, account_id=account.id, created_by_user_id=creator_id, test_category=category)
    return owner, viewer, account, category, expense


def test_accounts_patch_active_owner_can_rename(client, db_session, test_user_id):
    # Pass the fixed ID to your seed function
    owner = seed_user(db_session, id=UUID(test_user_id))
    acc = seed_account(db_session, status=AccountStatus.ACTIVE)
    seed_membership(db_session, user_id=owner.id, account_id=acc.id, role=MembershipRole.OWNER)

    resp = client.patch(
        f"/api/v1/accounts/{acc.id}", params={"current_user_id": str(owner.id)}, json={"name": "Renamed"}
    )
    assert_http(resp, 200)
    assert resp.json()["name"] == "Renamed"


def test_create_account_assigns_current_user_owner_and_seeds_categories(client, db_session, test_user_id):
    owner = seed_user(db_session, id=UUID(test_user_id))

    resp = client.post(
        "/api/v1/accounts/", headers={"X-User-Id": str(owner.id)}, json={"name": "Fresh Account", "status": "ACTIVE"}
    )
    assert_http(resp, 200)
    account_id = resp.json()["id"]

    members_resp = client.get(f"/api/v1/accounts/{account_id}/memberships", headers={"X-User-Id": str(owner.id)})
    assert_http(members_resp, 200)
    members = members_resp.json()
    assert len(members) == 1
    assert members[0]["user_id"] == str(owner.id)
    assert members[0]["role"] == "OWNER"

    categories_resp = client.get(f"/api/v1/accounts/{account_id}/categories", headers={"X-User-Id": str(owner.id)})
    assert_http(categories_resp, 200)
    category_names = {category["name"] for category in categories_resp.json()}
    assert {"Entertainment", "Miscellaneous"}.issubset(category_names)


def test_accounts_patch_active_owner_can_deactivate(client, db_session):
    owner = seed_user(db_session)
    acc = seed_account(db_session, status=AccountStatus.ACTIVE)
    seed_membership(db_session, user_id=owner.id, account_id=acc.id, role=MembershipRole.OWNER)

    resp = client.patch(
        f"/api/v1/accounts/{acc.id}", params={"current_user_id": str(owner.id)}, json={"status": "INACTIVE"}
    )
    assert_http(resp, 200)
    assert resp.json()["status"] == "INACTIVE"


def test_accounts_patch_inactive_owner_cannot_rename(client, db_session):
    owner = seed_user(db_session)
    acc = seed_account(db_session, status=AccountStatus.INACTIVE)
    seed_membership(db_session, user_id=owner.id, account_id=acc.id, role=MembershipRole.OWNER)

    resp = client.patch(f"/api/v1/accounts/{acc.id}", params={"current_user_id": str(owner.id)}, json={"name": "Nope"})
    assert_http(resp, 409, "ACCOUNT_INACTIVE")


def test_accounts_patch_inactive_owner_can_reactivate_only(client, db_session):
    owner = seed_user(db_session)
    acc = seed_account(db_session, status=AccountStatus.INACTIVE)
    seed_membership(db_session, user_id=owner.id, account_id=acc.id, role=MembershipRole.OWNER)

    # allowed: reactivation
    resp = client.patch(
        f"/api/v1/accounts/{acc.id}", params={"current_user_id": str(owner.id)}, json={"status": "ACTIVE"}
    )
    assert_http(resp, 200)
    assert resp.json()["status"] == "ACTIVE"

    # forbidden: reactivate + rename in same request
    acc2 = seed_account(db_session, status=AccountStatus.INACTIVE)
    seed_membership(db_session, user_id=owner.id, account_id=acc2.id, role=MembershipRole.OWNER)
    resp2 = client.patch(
        f"/api/v1/accounts/{acc2.id}",
        params={"current_user_id": str(owner.id)},
        json={"status": "ACTIVE", "name": "AlsoRename"},
    )
    assert_http(resp2, 409, "ACCOUNT_INACTIVE")


def test_accounts_patch_member_forbidden(client, db_session):
    owner = seed_user(db_session)
    member = seed_user(db_session)
    acc = seed_account(db_session, status=AccountStatus.ACTIVE)
    seed_membership(db_session, user_id=owner.id, account_id=acc.id, role=MembershipRole.OWNER)
    seed_membership(db_session, user_id=member.id, account_id=acc.id, role=MembershipRole.MEMBER)

    resp = client.patch(
        f"/api/v1/accounts/{acc.id}", params={"current_user_id": str(member.id)}, json={"name": "TryRename"}
    )
    assert_http(resp, 403, "ACCOUNT_UPDATE_FORBIDDEN")


# ============================================================
# Expense PATCH behavior (account state guard)
# ============================================================


def test_expense_update_blocked_when_account_inactive(client, db_session, test_category):
    owner = seed_user(db_session)
    acc = seed_account(db_session, status=AccountStatus.INACTIVE)
    seed_membership(db_session, user_id=owner.id, account_id=acc.id, role=MembershipRole.OWNER)
    cat = seed_category(db=db_session, account_id=acc.id, name=test_category.name, emoji=test_category.emoji)
    exp = seed_expense(db_session, account_id=acc.id, created_by_user_id=owner.id, test_category=cat)

    resp = client.patch(
        f"/api/v1/expenses/{exp.id}", params={"current_user_id": str(owner.id)}, json={"description": "new"}
    )
    assert_http(resp, 409, "ACCOUNT_INACTIVE")


def test_accounts_patch_no_fields_provided_returns_400(client, db_session):
    owner = seed_user(db_session)
    acc = seed_account(db_session, status=AccountStatus.ACTIVE)
    seed_membership(db_session, user_id=owner.id, account_id=acc.id, role=MembershipRole.OWNER)

    # CHANGE THIS: Remove the "status" field so the body is truly empty
    resp = client.patch(
        f"/api/v1/accounts/{acc.id}",
        params={"current_user_id": str(owner.id)},
        json={},  # This is what triggers the "NO_FIELDS_PROVIDED" error
    )

    assert_http(resp, 400, "ACCOUNT_UPDATE_NO_FIELDS_PROVIDED")


def test_accounts_patch_non_owner_returns_403(client, db_session):
    owner = seed_user(db_session)
    member = seed_user(db_session)
    acc = seed_account(db_session, status=AccountStatus.ACTIVE)

    seed_membership(db_session, user_id=owner.id, account_id=acc.id, role=MembershipRole.OWNER)
    seed_membership(db_session, user_id=member.id, account_id=acc.id, role=MembershipRole.MEMBER)

    resp = client.patch(
        f"/api/v1/accounts/{acc.id}", params={"current_user_id": str(member.id)}, json={"name": "try-rename"}
    )
    assert_http(resp, 403, "ACCOUNT_UPDATE_FORBIDDEN")


def test_expense_patch_no_fields_provided_returns_400(client, db_session, test_category):
    owner = seed_user(db_session)
    acc = seed_account(db_session, status=AccountStatus.ACTIVE)
    seed_membership(db_session, user_id=owner.id, account_id=acc.id, role=MembershipRole.OWNER)
    cat = seed_category(db=db_session, account_id=acc.id, name=test_category.name, emoji=test_category.emoji)
    exp = seed_expense(db_session, account_id=acc.id, created_by_user_id=owner.id, test_category=cat)

    resp = client.patch(
        f"/api/v1/expenses/{exp.id}",
        params={"current_user_id": str(owner.id)},
        json={},  # empty -> no fields provided
    )
    assert_http(resp, 400, "EXPENSE_UPDATE_NO_FIELDS_PROVIDED")


def test_account_list_only_returns_current_user_accounts(client, db_session):
    alice = seed_user(db_session)
    bob = seed_user(db_session)
    alice_account = seed_account(db_session, name="Alice Account")
    bob_account = seed_account(db_session, name="Bob Account")
    seed_membership(db_session, user_id=alice.id, account_id=alice_account.id, role=MembershipRole.OWNER)
    seed_membership(db_session, user_id=bob.id, account_id=bob_account.id, role=MembershipRole.OWNER)

    resp = client.get("/api/v1/accounts/", params={"current_user_id": str(alice.id)})

    assert_http(resp, 200)
    account_ids = {item["id"] for item in resp.json()}
    assert account_ids == {str(alice_account.id)}


def test_account_read_rejects_non_member(client, db_session):
    alice = seed_user(db_session)
    bob = seed_user(db_session)
    bob_account = seed_account(db_session)
    seed_membership(db_session, user_id=bob.id, account_id=bob_account.id, role=MembershipRole.OWNER)

    resp = client.get(f"/api/v1/accounts/{bob_account.id}", params={"current_user_id": str(alice.id)})

    assert_http(resp, 403, "USER_NOT_MEMBER_OF_THE_ACCOUNT")


def test_global_user_list_is_disabled_outside_local_prototype(client, monkeypatch):
    monkeypatch.setenv("DEV", "False")
    monkeypatch.setenv("TESTING", "False")
    monkeypatch.setenv("ALLOW_X_USER_ID_AUTH", "False")

    resp = client.get("/api/v1/users/")

    assert_http(resp, 403, "USER_LIST_FORBIDDEN")


def test_user_search_finds_exact_email_for_authenticated_user(client, db_session):
    current_user = seed_user(db_session)
    target_user = seed_user(db_session, email="target-user@example.com")

    resp = client.get(
        "/api/v1/users/search", params={"current_user_id": str(current_user.id), "email": target_user.email}
    )

    assert_http(resp, 200)
    assert [user["id"] for user in resp.json()] == [str(target_user.id)]


def test_user_read_allows_self_only(client, db_session):
    alice = seed_user(db_session)
    bob = seed_user(db_session)

    self_resp = client.get(f"/api/v1/users/{alice.id}", params={"current_user_id": str(alice.id)})
    other_resp = client.get(f"/api/v1/users/{bob.id}", params={"current_user_id": str(alice.id)})

    assert_http(self_resp, 200)
    assert self_resp.json()["id"] == str(alice.id)
    assert_http(other_resp, 403, "USER_READ_FORBIDDEN")


def test_expense_list_only_returns_current_user_account_expenses(client, db_session):
    alice = seed_user(db_session)
    bob = seed_user(db_session)
    alice_account = seed_account(db_session)
    bob_account = seed_account(db_session)
    seed_membership(db_session, user_id=alice.id, account_id=alice_account.id, role=MembershipRole.OWNER)
    seed_membership(db_session, user_id=bob.id, account_id=bob_account.id, role=MembershipRole.OWNER)
    alice_category = seed_category(db=db_session, account_id=alice_account.id, name="Alice General", emoji="A")
    bob_category = seed_category(db=db_session, account_id=bob_account.id, name="Bob General", emoji="B")
    alice_expense = seed_expense(
        db_session, account_id=alice_account.id, created_by_user_id=alice.id, test_category=alice_category
    )
    seed_expense(db_session, account_id=bob_account.id, created_by_user_id=bob.id, test_category=bob_category)

    resp = client.get("/api/v1/expenses/", params={"current_user_id": str(alice.id)})

    assert_http(resp, 200)
    expense_ids = {item["id"] for item in resp.json()}
    assert expense_ids == {str(alice_expense.id)}


def test_expense_read_rejects_non_member(client, db_session):
    alice = seed_user(db_session)
    bob = seed_user(db_session)
    bob_account = seed_account(db_session)
    seed_membership(db_session, user_id=bob.id, account_id=bob_account.id, role=MembershipRole.OWNER)
    bob_category = seed_category(db=db_session, account_id=bob_account.id, name="Bob General", emoji="B")
    bob_expense = seed_expense(
        db_session, account_id=bob_account.id, created_by_user_id=bob.id, test_category=bob_category
    )

    resp = client.get(f"/api/v1/expenses/{bob_expense.id}", params={"current_user_id": str(alice.id)})

    assert_http(resp, 403, "USER_NOT_MEMBER_OF_THE_ACCOUNT")


def test_viewer_can_read_account_expense(client, db_session):
    _, viewer, _, _, expense = _seed_viewer_expense_context(db_session)

    resp = client.get(f"/api/v1/expenses/{expense.id}", params={"current_user_id": str(viewer.id)})

    assert_http(resp, 200)
    assert resp.json()["id"] == str(expense.id)


def test_viewer_cannot_create_expense(client, db_session):
    _, viewer, account, category, _ = _seed_viewer_expense_context(db_session)

    resp = client.post(
        "/api/v1/expenses/",
        params={"current_user_id": str(viewer.id)},
        json={
            "account_id": str(account.id),
            "description": "Viewer create attempt",
            "amount": "12.00",
            "category_id": str(category.id),
            "expense_date": "2024-02-10",
            "currency": "EUR",
        },
    )

    assert_http(resp, 403, "ACCOUNT_MUTATION_FORBIDDEN")


def test_viewer_cannot_update_own_expense(client, db_session):
    _, viewer, _, _, expense = _seed_viewer_expense_context(db_session, viewer_is_creator=True)

    resp = client.patch(
        f"/api/v1/expenses/{expense.id}",
        params={"current_user_id": str(viewer.id)},
        json={"description": "Viewer edit attempt"},
    )

    assert_http(resp, 403, "ACCOUNT_MUTATION_FORBIDDEN")


def test_viewer_cannot_delete_own_expense(client, db_session):
    _, viewer, _, _, expense = _seed_viewer_expense_context(db_session, viewer_is_creator=True)

    resp = client.delete(f"/api/v1/expenses/{expense.id}", params={"current_user_id": str(viewer.id)})

    assert_http(resp, 403, "ACCOUNT_MUTATION_FORBIDDEN")


def test_viewer_cannot_approve_pending_expense(client, db_session):
    _, viewer, _, _, expense = _seed_viewer_expense_context(db_session)

    resp = client.patch(f"/api/v1/expenses/{expense.id}/approve", params={"current_user_id": str(viewer.id)})

    assert_http(resp, 403, "ACCOUNT_MUTATION_FORBIDDEN")
    db_session.refresh(expense)
    assert expense.status == ExpenseStatus.PENDING


def test_membership_list_only_returns_current_user_account_memberships(client, db_session):
    alice = seed_user(db_session)
    bob = seed_user(db_session)
    alice_account = seed_account(db_session)
    bob_account = seed_account(db_session)
    alice_membership = seed_membership(
        db_session, user_id=alice.id, account_id=alice_account.id, role=MembershipRole.OWNER
    )
    seed_membership(db_session, user_id=bob.id, account_id=bob_account.id, role=MembershipRole.OWNER)

    resp = client.get("/api/v1/memberships/", params={"current_user_id": str(alice.id)})

    assert_http(resp, 200)
    membership_ids = {item["id"] for item in resp.json()}
    assert membership_ids == {str(alice_membership.id)}


def test_membership_read_rejects_non_member(client, db_session):
    alice = seed_user(db_session)
    bob = seed_user(db_session)
    bob_account = seed_account(db_session)
    bob_membership = seed_membership(db_session, user_id=bob.id, account_id=bob_account.id, role=MembershipRole.OWNER)

    resp = client.get(f"/api/v1/memberships/{bob_membership.id}", params={"current_user_id": str(alice.id)})

    assert_http(resp, 403, "USER_NOT_MEMBER_OF_THE_ACCOUNT")


def test_financial_profile_read_rejects_non_member(client, db_session):
    alice = seed_user(db_session)
    bob = seed_user(db_session)
    bob_account = seed_account(db_session)
    seed_membership(db_session, user_id=bob.id, account_id=bob_account.id, role=MembershipRole.OWNER)
    db_session.add(FinancialProfile(account_id=bob_account.id))
    db_session.flush()

    resp = client.get(f"/api/v1/accounts/{bob_account.id}/financial-profile", params={"current_user_id": str(alice.id)})

    assert_http(resp, 403, "USER_NOT_MEMBER_OF_THE_ACCOUNT")


def test_budget_summary_rejects_non_member_account(client, db_session):
    alice = seed_user(db_session)
    bob = seed_user(db_session)
    bob_account = seed_account(db_session)
    seed_membership(db_session, user_id=bob.id, account_id=bob_account.id, role=MembershipRole.OWNER)

    resp = client.get(
        "/api/v1/summaries/budget-status", params={"account_id": str(bob_account.id), "current_user_id": str(alice.id)}
    )

    assert_http(resp, 403, "USER_NOT_MEMBER_OF_THE_ACCOUNT")
