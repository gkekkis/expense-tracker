"""Module containign User session functionalities."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Sequence
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session  # noqa: TCH002

from ..db.models.account import Account
from ..db.models.expense import Expense
from ..db.models.membership import Membership
from ..db.models.user import User
from ..domain.currencies.currency import Currency
from ..domain.memberships.membership import MembershipRole
from ..domain.operations import Operation
from ..domain.policies.account_state import ensure_account_mutable
from ..errors.errors import (
    AccountDoesNotExistError,
    ExpenseDeleteForbiddenError,
    ExpenseDoesNotExistError,
    ExpenseUpdateForbiddenError,
    ExpenseUpdateNoFieldsProvidedError,
    UserDoesNotExistError,
    UserNotMemberOfTheAccountError,
)
from ..schemas.expense import (
    ExpenseCategory,
    ExpenseCreate,  # noqa: TCH001
    ExpenseFilterParams,
)
from .account_service import get_account_by_id


def create_expense(session: Session, expense_in: ExpenseCreate, created_by_user_id: UUID | None) -> Expense:
    # Check if account exists
    statement = select(1).where(Account.id == expense_in.account_id).limit(1)
    result = session.scalar(statement)

    if result is None:
        raise AccountDoesNotExistError(account_id=expense_in.account_id)

    if created_by_user_id is not None:
        # Check if user exists
        db_user = session.get(User, created_by_user_id)
        if db_user is None:
            raise UserDoesNotExistError(user_id=created_by_user_id)

        # Check if user is a member of the account
        statement = (
            select(1)
            .where(Membership.user_id == created_by_user_id)
            .where(Membership.account_id == expense_in.account_id)
            .limit(1)
        )

        result = session.scalar(statement)

        if result is None:
            raise UserNotMemberOfTheAccountError(user_id=created_by_user_id, account_id=expense_in.account_id)

    db_expense = Expense(
        account_id=expense_in.account_id,
        created_by_user_id=created_by_user_id,
        description=expense_in.description,
        amount=expense_in.amount,
        category=expense_in.category,
        expense_date=expense_in.expense_date,
        currency=expense_in.currency,
    )

    session.add(db_expense)
    session.flush()

    return db_expense


def get_all_expenses(session: Session) -> Sequence[Expense]:
    return session.scalars(select(Expense)).all()


def get_expense_by_id(session: Session, expense_id: UUID) -> Expense:
    db_expense = session.get(Expense, expense_id)
    if db_expense is None:
        raise ExpenseDoesNotExistError(expense_id=expense_id)
    return db_expense


def update_expense_by_id(
    session: Session,
    expense_id: UUID,
    current_user_id: UUID,
    description: str | None = None,
    amount: Decimal | None = None,
    category: ExpenseCategory | None = None,
    expense_date: date | None = None,
    currency: Currency | None = None,
) -> Expense:
    db_expense = session.get(Expense, expense_id)
    # Check if account is ACTIVE
    account_id = db_expense.account_id
    statement = select(Account.status).where(Account.id == account_id)
    account_status = session.scalar(statement)

    # Check if account exists
    if session.get(Account, account_id) is None:
        raise AccountDoesNotExistError(account_id=account_id)

    # If exists use helper function to check if it is active. If not raise error
    ensure_account_mutable(account_id=account_id, account_status=account_status, operation=Operation.EXPENSE_UPDATE)

    if db_expense is None:
        raise ExpenseDoesNotExistError(expense_id=expense_id)

    if all(value is None for value in [description, amount, category, expense_date]):
        raise ExpenseUpdateNoFieldsProvidedError(expense_id=expense_id)

    # Check if user is a member of the account
    statement = (
        select(Expense.account_id)
        .where(Membership.user_id == current_user_id)
        .where(Membership.account_id == db_expense.account_id)
        .limit(1)
    )

    is_member = session.scalar(statement) is not None

    if not is_member:
        raise UserNotMemberOfTheAccountError(user_id=current_user_id, account_id=db_expense.account_id)

    statement = (
        select(1).where(
            Membership.user_id == current_user_id,
            Membership.account_id == db_expense.account_id,
            Membership.role == MembershipRole.OWNER,
        )
    ).limit(1)
    current_user_is_owner = session.scalar(statement) is not None
    if all([not db_expense.created_by_user_id == current_user_id, not current_user_is_owner]):
        raise ExpenseUpdateForbiddenError(
            user_id=current_user_id, expense_id=expense_id, account_id=db_expense.account_id
        )

    if description is not None:
        db_expense.description = description
    if amount is not None:
        db_expense.amount = amount
    if category is not None:
        db_expense.category = category
    if expense_date is not None:
        db_expense.expense_date = expense_date
    if currency is not None:
        db_expense.currency = currency

    session.flush()

    return db_expense


def delete_expense_by_id(session: Session, expense_id: UUID, current_user_id: UUID) -> None:
    db_expense = session.get(Expense, expense_id)
    if db_expense is None:
        raise ExpenseDoesNotExistError(expense_id=expense_id)

    # Check if user is a member of the account
    statement = (
        select(1)
        .where(Membership.user_id == current_user_id)
        .where(Membership.account_id == db_expense.account_id)
        .limit(1)
    )

    is_member = session.scalar(statement) is not None

    if not is_member:
        raise UserNotMemberOfTheAccountError(user_id=current_user_id, account_id=db_expense.account_id)

    statement = (
        select(1).where(
            Membership.user_id == current_user_id,
            Membership.account_id == db_expense.account_id,
            Membership.role == MembershipRole.OWNER,
        )
    ).limit(1)
    current_user_is_owner = session.scalar(statement) is not None
    if all([not db_expense.created_by_user_id == current_user_id, not current_user_is_owner]):
        raise ExpenseDeleteForbiddenError(
            user_id=current_user_id, expense_id=expense_id, account_id=db_expense.account_id
        )

    session.delete(db_expense)
    session.flush()
    return None


def get_filtered_expenses(session: Session, params: ExpenseFilterParams, current_user_id: UUID):
    # 1. Reuse existing account logic
    db_account = get_account_by_id(session=session, account_id=params.account_id)

    ensure_account_mutable(
        account_id=params.account_id, account_status=db_account.status, operation=Operation.EXPENSE_READ
    )

    # 2. Membership Check
    is_a_member = (
        session.scalar(
            select(1).where(Membership.account_id == params.account_id, Membership.user_id == current_user_id).limit(1)
        )
        is not None
    )

    if not is_a_member:
        raise UserNotMemberOfTheAccountError(user_id=current_user_id, account_id=params.account_id)

    # 3. Base Query
    query = select(Expense).where(Expense.account_id == params.account_id)

    # 4. Robust Search Logic (FTS)
    search_query = getattr(params, "search_query", None)
    if search_query and isinstance(search_query, str):
        search_input = search_query.strip()
        if search_input:
            search_str = f"{search_input}:*"
            query = query.where(
                func.to_tsvector("english", Expense.description).op("@@")(func.to_tsquery("english", search_str))
            )

    # 5. Apply Filters
    if params.start_date:
        query = query.where(Expense.expense_date >= params.start_date)
    if params.category:
        query = query.where(Expense.category == params.category)

    # 6. Aggregation (Get Total Count before Pagination)
    subq = query.subquery()
    total_count = session.execute(select(func.count()).select_from(subq)).scalar() or 0

    # 7. Final Results (Paginated)
    final_query = query.order_by(Expense.expense_date.desc()).offset(params.offset).limit(params.limit)
    results = session.execute(final_query).scalars().all()

    return results, total_count, 0
