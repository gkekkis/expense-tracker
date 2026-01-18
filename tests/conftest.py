import os
from datetime import date
from pathlib import Path
from uuid import UUID, uuid4

import pytest
import pytest_asyncio
from dotenv import load_dotenv
from httpx import ASGITransport, AsyncClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user_id, get_db
from app.db.base import Base
from app.db.models.account import Account
from app.db.models.expense import Expense
from app.db.models.membership import Membership
from app.db.models.user import User  # noqa: F401
from app.domain.accounts.account import AccountStatus
from app.domain.currencies.currency import Currency
from app.domain.expenses.expense import ExpenseCategory
from app.domain.users.user import UserStatus
from app.main import app

# Load environment
dotenv_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path)
SQLALCHEMY_DATABASE_URL = os.getenv("PYTEST_DATABASE_URL")


@pytest.fixture(scope="session")
def engine():
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    with engine.begin() as conn:
        conn.execute(text("DROP SCHEMA public CASCADE; CREATE SCHEMA public;"))
    Base.metadata.create_all(bind=engine)
    yield engine


@pytest.fixture(scope="function")
def db_session(engine):
    connection = engine.connect()
    # Begin the outer transaction
    transaction = connection.begin()
    # Create a session bound to the connection
    session = Session(bind=connection, join_transaction_mode="create_savepoint")

    yield session

    session.close()
    # Roll back the outer transaction to wipe everything clean
    transaction.rollback()
    connection.close()


@pytest_asyncio.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac


# --- CRITICAL FIX: Consistent User ID ---
@pytest.fixture
def test_user_id():
    """Consistent ID used for both Auth and DB records."""
    return "6f3a032e-cd99-492e-8b7f-67037faaaef6"


@pytest.fixture
def user_token_headers(test_user_id):
    return {"Authorization": "Bearer fake-token", "X-User-Id": test_user_id}


from fastapi import Request


@pytest.fixture(autouse=True)
def override_dependencies(db_session, test_user_id):
    # 1. Override database
    app.dependency_overrides[get_db] = lambda: db_session

    # 2. Smart Auth Override
    def get_test_user_id(request: Request):
        # First, check if the test passed a specific ID in the query params
        user_id = request.query_params.get("current_user_id")
        if user_id:
            return UUID(user_id)
        # Otherwise, check the X-User-Id header
        user_id = request.headers.get("X-User-Id")
        if user_id:
            return UUID(user_id)
        # Fallback to the default test user
        return UUID(test_user_id)

    app.dependency_overrides[get_current_user_id] = get_test_user_id

    yield
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db_session, test_user_id):
    uid = UUID(test_user_id)
    # Check if user already exists to prevent UniqueViolation
    existing_user = db_session.query(User).filter(User.id == uid).first()
    if existing_user:
        return existing_user

    user = User(id=uid, name="Test User", email="test@example.com", status=UserStatus.ACTIVE)
    db_session.add(user)
    db_session.flush()
    return user


@pytest.fixture
def test_account(db_session, test_user):
    account = Account(id=uuid4(), name="Test Account", status=AccountStatus.ACTIVE)
    db_session.add(account)
    db_session.flush()

    membership = Membership(id=uuid4(), user_id=test_user.id, account_id=account.id, role="OWNER")
    db_session.add(membership)

    db_session.flush()  # CHANGED: commit() -> flush()
    db_session.refresh(account)
    return account


# --- Remaining fixtures ---
@pytest.fixture
def test_expenses(db_session, test_account):
    e1 = Expense(
        id=uuid4(),
        account_id=test_account.id,
        description="Weekly Shop",
        amount=100.0,
        currency=Currency.EUR,
        category=ExpenseCategory.GROCERIES,  # Doesn't match search
        expense_date=date.today(),
    )
    e2 = Expense(
        id=uuid4(),
        account_id=test_account.id,
        description="Monthly Rent",
        amount=1200.0,
        currency=Currency.USD,
        category=ExpenseCategory.RENTAL,  # Doesn't match search
        expense_date=date.today(),
    )
    # ADD THIS ONE:
    e3 = Expense(
        id=uuid4(),
        account_id=test_account.id,
        description="Internet Bill",
        amount=50.0,
        currency=Currency.EUR,
        category=ExpenseCategory.BILLS,  # MATCHES SEARCH!
        expense_date=date.today(),
    )

    db_session.add_all([e1, e2, e3])
    db_session.flush()
    return [e1, e2, e3]


@pytest.fixture
def seed_currency_rates(db_session):
    """Seed exchange rates for testing (Base is EUR)"""
    from app.db.models.currency import CurrencyRate
    from app.domain.currencies.currency import Currency

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
