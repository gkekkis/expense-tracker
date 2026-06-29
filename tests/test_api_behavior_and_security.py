import os
from uuid import UUID

from conftest import assert_http, seed_account, seed_category, seed_expense, seed_membership, seed_user
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

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
