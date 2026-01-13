from datetime import date
from uuid import UUID, uuid4

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.api.dependencies import get_db
from app.db.base import Base
from app.db.models.account import Account
from app.db.models.expense import Expense
from app.db.models.membership import Membership, MembershipRole
from app.domain.accounts.account import AccountStatus
from app.domain.expenses.expense import ExpenseCategory
from app.main import app

SQLALCHEMY_DATABASE_URL = "sqlite:///./tests/test.db"


@pytest.fixture(scope="session")
def engine():
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session(engine):
    connection = engine.connect()
    transaction = connection.begin()
    session = sessionmaker(bind=connection)()
    yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest_asyncio.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac


@pytest.fixture
def test_user_id():
    # This MUST match the ID used in your membership/ownership logic
    return "6f3a032e-cd99-492e-8b7f-67037faaaef6"


@pytest.fixture
def user_token_headers(test_user_id):
    return {"Authorization": "Bearer fake-token", "X-User-Id": test_user_id}


@pytest.fixture(autouse=True)
def override_get_db(db_session):
    def _get_db_override():
        yield db_session

    app.dependency_overrides[get_db] = _get_db_override
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def test_account(db_session, test_user_id):
    """Creates an account and links the test user as the OWNER."""
    account = Account(
        id=uuid4(), name="Test Account 1", status=AccountStatus.ACTIVE, created_at=date.today(), updated_at=date.today()
    )
    db_session.add(account)
    db_session.flush()  # Get the account ID without committing yet

    # IMPORTANT: Link the user to the account so the 403 check passes
    # If your app uses a 'Membership' table for permissions:
    membership = Membership(
        user_id=UUID(test_user_id),
        account_id=account.id,
        role=MembershipRole.OWNER,  # or "admin" depending on your model
    )
    db_session.add(membership)

    db_session.commit()
    return account


@pytest.fixture
def test_expenses(db_session, test_account):
    e1 = Expense(
        account_id=test_account.id,
        description="Weekly Shop",
        amount=100.0,
        category=ExpenseCategory.BILLS,
        expense_date=date.today(),
    )
    e2 = Expense(
        account_id=test_account.id,
        description="Monthly Rent",
        amount=1200.0,
        category=ExpenseCategory.ENTERTAINMENT,
        expense_date=date.today(),
    )
    db_session.add_all([e1, e2])
    db_session.commit()
    return [e1, e2]
