import os
from datetime import date, datetime, timezone
from decimal import Decimal
from pathlib import Path
from uuid import UUID, uuid4

import pytest
from dotenv import load_dotenv
from fastapi import Request
from sqlalchemy import create_engine, text
from sqlalchemy.inspection import inspect as sa_inspect
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user_id, get_db
from app.db.base import Base
from app.db.models.account import Account
from app.db.models.category import Category
from app.db.models.currency import CurrencyRate
from app.db.models.expense import Expense
from app.db.models.membership import Membership, MembershipRole
from app.db.models.user import User
from app.domain.accounts.account import AccountStatus
from app.domain.currencies.currency import Currency
from app.domain.expenses.expense import ExpenseStatus
from app.domain.users.user import UserStatus
from app.main import app

# Load environment
dotenv_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path)
DATABASE_URL = os.getenv("PYTEST_DATABASE_URL")


# --- Database Setup ---
@pytest.fixture(scope="session")
def engine():
    if not DATABASE_URL:
        raise RuntimeError("Set PYTEST_DATABASE_URL for tests.")

    _engine = create_engine(DATABASE_URL)

    # Clean start: Clear the public schema (Postgres specific)
    with _engine.begin() as conn:
        conn.execute(text("DROP SCHEMA public CASCADE; CREATE SCHEMA public;"))

    Base.metadata.create_all(bind=_engine)
    yield _engine
    Base.metadata.drop_all(bind=_engine)


@pytest.fixture(scope="function")
def db_session(engine):
    """The gold standard DB fixture: one transaction per test, rolled back at the end."""
    connection = engine.connect()
    transaction = connection.begin()
    # join_transaction_mode="create_savepoint" allows code to call .commit()
    # without actually committing the outer test transaction
    session = Session(bind=connection, join_transaction_mode="create_savepoint")

    yield session

    session.close()
    transaction.rollback()
    connection.close()


# --- API Client Setup ---
@pytest.fixture()
def client(db_session):
    """Synchronous client for testing FastAPI endpoints."""
    from fastapi.testclient import TestClient

    # Ensure the dependency override is active for this client
    app.dependency_overrides[get_db] = lambda: db_session

    with TestClient(app) as c:
        yield c
    # Clean up is handled by the autouse override_dependencies,
    # but we'll clear here to be safe.
    app.dependency_overrides.clear()


# --- Auth & Dependency Overrides ---
@pytest.fixture
def test_user_id():
    return "6f3a032e-cd99-492e-8b7f-67037faaaef6"


@pytest.fixture
def user_token_headers(test_user_id):
    return {"Authorization": "Bearer fake-token", "X-User-Id": test_user_id}


@pytest.fixture(autouse=True)
def override_dependencies(db_session, test_user_id):
    # Swap real DB for test DB
    app.dependency_overrides[get_db] = lambda: db_session

    # Swap real Auth for test Auth
    def get_test_user_id(request: Request):
        user_id = request.query_params.get("current_user_id") or request.headers.get("X-User-Id")
        return UUID(user_id) if user_id else UUID(test_user_id)

    app.dependency_overrides[get_current_user_id] = get_test_user_id
    yield
    app.dependency_overrides.clear()


# --- Assertions ---
def assert_http(resp, expected_status: int, expected_error_code: str | None = None):
    assert resp.status_code == expected_status, f"Expected {expected_status}, got {resp.status_code}: {resp.text}"
    if expected_error_code is not None:
        body = resp.json()
        assert body.get("error_code") == expected_error_code, f"Expected {expected_error_code}, got {body}"


# --- Seed Fixtures (The reusable parts) ---
@pytest.fixture
def test_user(db_session, test_user_id):
    uid = UUID(test_user_id)
    user = User(id=uid, name="Test User", email="test@example.com", status=UserStatus.ACTIVE)
    db_session.add(user)
    db_session.flush()
    return user


@pytest.fixture
def test_users(db_session):
    u1 = User(id=uuid4(), name="User One", email="one@test.com", status=UserStatus.ACTIVE)
    u2 = User(id=uuid4(), name="User Two", email="two@test.com", status=UserStatus.ACTIVE)
    db_session.add_all([u1, u2])
    db_session.flush()
    return [u1, u2]


# --- 2. ACCOUNT SET ---
@pytest.fixture
def test_account(db_session, test_user):
    """Creates an account and automatically makes the test_user the owner."""
    account = Account(id=uuid4(), name="Test Account", status=AccountStatus.ACTIVE)
    db_session.add(account)
    db_session.flush()

    # Create the link immediately
    m = Membership(id=uuid4(), user_id=test_user.id, account_id=account.id, role=MembershipRole.OWNER)
    db_session.add(m)
    db_session.flush()

    return account


@pytest.fixture
def test_accounts(db_session):
    a1 = Account(id=uuid4(), name="Account A", status=AccountStatus.ACTIVE)
    a2 = Account(id=uuid4(), name="Account B", status=AccountStatus.ACTIVE)
    db_session.add_all([a1, a2])
    db_session.flush()
    return [a1, a2]


# --- 3. MEMBERSHIP SET ---
@pytest.fixture
def test_membership(db_session, test_user, test_account):
    m = Membership(id=uuid4(), user_id=test_user.id, account_id=test_account.id, role=MembershipRole.OWNER)
    db_session.add(m)
    db_session.flush()
    return m


@pytest.fixture
def test_memberships(db_session, test_users, test_account):
    m1 = Membership(id=uuid4(), user_id=test_users[0].id, account_id=test_account.id, role=MembershipRole.OWNER)
    m2 = Membership(id=uuid4(), user_id=test_users[1].id, account_id=test_account.id, role=MembershipRole.MEMBER)
    db_session.add_all([m1, m2])
    db_session.flush()
    return [m1, m2]


# --- 4. CATEGORY SET ---
@pytest.fixture
def test_category(db_session, test_account):
    cat = Category(id=uuid4(), account_id=test_account.id, name="General", emoji="💰")
    db_session.add(cat)
    db_session.flush()
    return cat


@pytest.fixture
def test_categories(db_session, test_account):
    c1 = Category(id=uuid4(), account_id=test_account.id, name="Food", emoji="🍕")
    c2 = Category(id=uuid4(), account_id=test_account.id, name="Transport", emoji="🚗")
    db_session.add_all([c1, c2])
    db_session.flush()
    return [c1, c2]


# --- 5. EXPENSE SET ---
@pytest.fixture
def test_expense(db_session, test_account, test_category, test_user):
    exp = Expense(
        id=uuid4(),
        account_id=test_account.id,
        created_by_user_id=test_user.id,
        description="Internet Bill",
        amount=Decimal("10.00"),
        currency=Currency.EUR,
        category_id=test_category.id,
        expense_date=date.today(),
        status=ExpenseStatus.COMPLETED,
    )
    db_session.add(exp)
    db_session.flush()
    return exp


@pytest.fixture
def test_expenses(db_session, test_account, test_category, test_user):
    e1 = Expense(
        id=uuid4(),
        account_id=test_account.id,
        created_by_user_id=test_user.id,
        description="Expense One",
        amount=Decimal("50.00"),
        currency=Currency.EUR,
        category_id=test_category.id,
        expense_date=date.today(),
        status=ExpenseStatus.COMPLETED,
    )
    e2 = Expense(
        id=uuid4(),
        account_id=test_account.id,
        created_by_user_id=test_user.id,
        description="Expense Two",
        amount=Decimal("100.00"),
        currency=Currency.USD,
        category_id=test_category.id,
        expense_date=date.today(),
        status=ExpenseStatus.COMPLETED,
    )
    db_session.add_all([e1, e2])
    db_session.flush()
    return [e1, e2]


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


def seed_currency_rates(db_session):
    """Seed exchange rates for testing (Base is EUR)"""
    from app.domain.currencies.currency import Currency

    print("DEBUG: `seed_currency_rates` fixture Loaded")
    rates = [
        CurrencyRate(code=Currency.EUR, rate=1.0),
        # 1 EUR = 1.08 USD (so 1 USD = ~0.925 EUR)
        CurrencyRate(code=Currency.USD, rate=1.08),
        # 1 EUR = 0.85 GBP (so 1 GBP = ~1.176 EUR)
        CurrencyRate(code=Currency.GBP, rate=0.85),
    ]

    for rate in rates:
        db_session.add(rate)

    db_session.flush()
    return rates


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


def seed_expense(db, *, account_id, created_by_user_id, test_category):
    e = Expense(
        id=uuid4(),
        account_id=account_id,
        created_by_user_id=created_by_user_id,
        description="seed",
        amount=Decimal("10.00"),
        category_id=test_category.id,
        status=ExpenseStatus.PENDING,
        expense_date=date.today(),
        currency=Currency.EUR,
    )
    db.add(e)
    db.flush()
    return e


def seed_category(db, *, account_id, name, emoji):
    c = Category(account_id=account_id, name=name, emoji=emoji)
    db.add(c)
    db.flush()
    return c
