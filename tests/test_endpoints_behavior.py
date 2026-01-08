import os
from datetime import date, datetime, timezone
from decimal import Decimal
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.inspection import inspect as sa_inspect
from sqlalchemy.orm import sessionmaker

from app.api.dependencies import get_db
from app.db.base import Base  # declarative base
from app.db.models.account import Account
from app.db.models.expense import Expense  # adjust if different
from app.db.models.membership import Membership, MembershipRole
from app.db.models.user import User  # adjust if different
from app.domain.accounts.account import AccountStatus
from app.domain.expenses.expense import ExpenseCategory  # adjust if different

# ---- Import your FastAPI app and DB base/models ----
# Adjust imports to match your project layout
from app.main import app  # must expose FastAPI instance

# ---------- Test DB setup ----------
DATABASE_URL = os.getenv("TEST_DATABASE_URL") or os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("Set TEST_DATABASE_URL (preferred) or DATABASE_URL for tests.")

engine = create_engine(DATABASE_URL)
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


@pytest.fixture(scope="session", autouse=True)
def create_schema():
    # For a dedicated TEST DB only. Do NOT point this at prod.
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def db():
    session = TestingSessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


@pytest.fixture()
def client(db):
    # Override FastAPI dependency to use the test session
    def _override_get_db():
        yield db

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


# ---------- Seed helpers ----------
def _autofill_required_fields(model_cls, explicit: dict):
    """
    Fill NOT NULL columns that have no default/server_default, unless explicitly provided.
    Works well for tests where you only want to care about a subset of fields.
    """
    data = dict(explicit)
    mapper = sa_inspect(model_cls)

    for col in mapper.columns:
        key = col.key

        # already provided
        if key in data:
            continue

        # allow NULL
        if col.nullable:
            continue

        # has client-side or server-side default
        if col.default is not None or col.server_default is not None:
            continue

        # primary key: let explicit handle it (or DB default)
        if col.primary_key:
            continue

        # crude but effective type-based defaults
        col_type = col.type
        type_name = col_type.__class__.__name__.lower()

        if "uuid" in type_name:
            data[key] = uuid4()
        elif "bool" in type_name:
            data[key] = False
        elif "int" in type_name:
            data[key] = 1
        elif "numeric" in type_name or "decimal" in type_name:
            data[key] = Decimal("1.00")
        elif "date" in type_name and "time" not in type_name:
            data[key] = date.today()
        elif "datetime" in type_name or "timestamp" in type_name:
            data[key] = datetime.now(timezone.utc)
        elif "enum" in type_name:
            # choose first enum value
            enum_cls = getattr(col_type, "enum_class", None)
            if enum_cls is not None:
                data[key] = list(enum_cls)[0]
            else:
                # last resort: string
                data[key] = "test"
        else:
            # string-ish fallback
            if "email" in key.lower():
                data[key] = f"{uuid4().hex}@test.local"
            else:
                data[key] = f"test-{key}-{uuid4().hex[:8]}"

    return data


def seed_user(db, *, user_id=None, **overrides):
    explicit = {"id": user_id or uuid4(), **overrides}
    data = _autofill_required_fields(User, explicit)
    u = User(**data)
    db.add(u)
    db.flush()
    return u


def seed_account(db, *, status=AccountStatus.ACTIVE, name=None):
    a = Account(id=uuid4(), name=name or f"acc-{uuid4().hex[:8]}", status=status)
    db.add(a)
    db.flush()
    return a


def seed_membership(db, *, user_id, account_id, role):
    m = Membership(id=uuid4(), user_id=user_id, account_id=account_id, role=role)
    db.add(m)
    db.flush()
    return m


def seed_expense(db, *, account_id, created_by_user_id):
    e = Expense(
        id=uuid4(),
        account_id=account_id,
        created_by_user_id=created_by_user_id,
        description="seed",
        amount=Decimal("10.00"),
        category=next(iter(ExpenseCategory)),
        expense_date=date.today(),
    )
    db.add(e)
    db.flush()
    return e


# ---------- Assertion helper (clear failures) ----------
def assert_http(resp, expected_status: int, expected_error_code: str | None = None):
    assert resp.status_code == expected_status, f"Expected {expected_status}, got {resp.status_code}: {resp.text}"
    if expected_error_code is not None:
        body = resp.json()
        assert body.get("error_code") == expected_error_code, f"Expected {expected_error_code}, got {body}"


# ============================================================
# Accounts PATCH behavior
# ============================================================


def test_accounts_patch_active_owner_can_rename(client, db):
    owner = seed_user(db)
    acc = seed_account(db, status=AccountStatus.ACTIVE)
    seed_membership(db, user_id=owner.id, account_id=acc.id, role=MembershipRole.OWNER)

    resp = client.patch(
        f"/api/v1/accounts/{acc.id}", params={"current_user_id": str(owner.id)}, json={"name": "Renamed"}
    )
    assert_http(resp, 200)
    assert resp.json()["name"] == "Renamed"


def test_accounts_patch_active_owner_can_deactivate(client, db):
    owner = seed_user(db)
    acc = seed_account(db, status=AccountStatus.ACTIVE)
    seed_membership(db, user_id=owner.id, account_id=acc.id, role=MembershipRole.OWNER)

    resp = client.patch(
        f"/api/v1/accounts/{acc.id}", params={"current_user_id": str(owner.id)}, json={"status": "INACTIVE"}
    )
    assert_http(resp, 200)
    assert resp.json()["status"] == "INACTIVE"


def test_accounts_patch_inactive_owner_cannot_rename(client, db):
    owner = seed_user(db)
    acc = seed_account(db, status=AccountStatus.INACTIVE)
    seed_membership(db, user_id=owner.id, account_id=acc.id, role=MembershipRole.OWNER)

    resp = client.patch(f"/api/v1/accounts/{acc.id}", params={"current_user_id": str(owner.id)}, json={"name": "Nope"})
    assert_http(resp, 409, "ACCOUNT_INACTIVE")


def test_accounts_patch_inactive_owner_can_reactivate_only(client, db):
    owner = seed_user(db)
    acc = seed_account(db, status=AccountStatus.INACTIVE)
    seed_membership(db, user_id=owner.id, account_id=acc.id, role=MembershipRole.OWNER)

    # allowed: reactivation
    resp = client.patch(
        f"/api/v1/accounts/{acc.id}", params={"current_user_id": str(owner.id)}, json={"status": "ACTIVE"}
    )
    assert_http(resp, 200)
    assert resp.json()["status"] == "ACTIVE"

    # forbidden: reactivate + rename in same request
    acc2 = seed_account(db, status=AccountStatus.INACTIVE)
    seed_membership(db, user_id=owner.id, account_id=acc2.id, role=MembershipRole.OWNER)
    resp2 = client.patch(
        f"/api/v1/accounts/{acc2.id}",
        params={"current_user_id": str(owner.id)},
        json={"status": "ACTIVE", "name": "AlsoRename"},
    )
    assert_http(resp2, 409, "ACCOUNT_INACTIVE")


def test_accounts_patch_member_forbidden(client, db):
    owner = seed_user(db)
    member = seed_user(db)
    acc = seed_account(db, status=AccountStatus.ACTIVE)
    seed_membership(db, user_id=owner.id, account_id=acc.id, role=MembershipRole.OWNER)
    seed_membership(db, user_id=member.id, account_id=acc.id, role=MembershipRole.MEMBER)

    resp = client.patch(
        f"/api/v1/accounts/{acc.id}", params={"current_user_id": str(member.id)}, json={"name": "TryRename"}
    )
    assert_http(resp, 403, "ACCOUNT_UPDATE_FORBIDDEN")


# ============================================================
# Expense PATCH behavior (account state guard)
# ============================================================


def test_expense_update_blocked_when_account_inactive(client, db):
    owner = seed_user(db)
    acc = seed_account(db, status=AccountStatus.INACTIVE)
    seed_membership(db, user_id=owner.id, account_id=acc.id, role=MembershipRole.OWNER)
    exp = seed_expense(db, account_id=acc.id, created_by_user_id=owner.id)

    resp = client.patch(
        f"/api/v1/expenses/{exp.id}", params={"current_user_id": str(owner.id)}, json={"description": "new"}
    )
    assert_http(resp, 409, "ACCOUNT_INACTIVE")


def test_accounts_patch_no_fields_provided_returns_400(client, db):
    owner = seed_user(db)
    acc = seed_account(db, status=AccountStatus.ACTIVE)
    seed_membership(db, user_id=owner.id, account_id=acc.id, role=MembershipRole.OWNER)

    # empty JSON body -> no fields provided
    resp = client.patch(f"/api/v1/accounts/{acc.id}", params={"current_user_id": str(owner.id)}, json={})
    assert_http(resp, 400, "ACCOUNT_UPDATE_NO_FIELDS_PROVIDED")


def test_accounts_patch_non_owner_returns_403(client, db):
    owner = seed_user(db)
    member = seed_user(db)
    acc = seed_account(db, status=AccountStatus.ACTIVE)

    seed_membership(db, user_id=owner.id, account_id=acc.id, role=MembershipRole.OWNER)
    seed_membership(db, user_id=member.id, account_id=acc.id, role=MembershipRole.MEMBER)

    resp = client.patch(
        f"/api/v1/accounts/{acc.id}", params={"current_user_id": str(member.id)}, json={"name": "try-rename"}
    )
    assert_http(resp, 403, "ACCOUNT_UPDATE_FORBIDDEN")


def test_expense_patch_no_fields_provided_returns_400(client, db):
    owner = seed_user(db)
    acc = seed_account(db, status=AccountStatus.ACTIVE)
    seed_membership(db, user_id=owner.id, account_id=acc.id, role=MembershipRole.OWNER)

    exp = seed_expense(db, account_id=acc.id, created_by_user_id=owner.id)

    resp = client.patch(
        f"/api/v1/expenses/{exp.id}",
        params={"current_user_id": str(owner.id)},
        json={},  # empty -> no fields provided
    )
    assert_http(resp, 400, "EXPENSE_UPDATE_NO_FIELDS_PROVIDED")
