"""Module containing User session functionalities."""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

from typing import Sequence  # noqa: E402
from uuid import UUID  # noqa: E402, TCH003

from sqlalchemy import select  # noqa: E402
from sqlalchemy.orm import Session  # noqa: TCH002, E402

from ..db.models.account import Account  # noqa: E402
from ..db.models.expense import Expense  # noqa: E402
from ..db.models.membership import Membership, MembershipRole  # noqa: E402
from ..domain.accounts.account import AccountStatus  # noqa: E402
from ..domain.operations import Operation  # noqa: E402
from ..domain.policies.account_state import (  # noqa: E402
    ensure_account_mutable,
    ensure_inactive_account_reactivation_only,
)
from ..errors.errors import (  # noqa: E402
    AccountDoesNotExistError,
    AccountUpdateForbiddenError,
    AccountUpdateNoFieldsProvidedError,
    UserNotMemberOfTheAccountError,
)
from ..schemas.account import AccountCreate  # noqa: TCH001, E402


def create_account(session: Session, account_in: AccountCreate) -> Account:
    db_account = Account(name=account_in.name, status=account_in.status)

    session.add(db_account)
    session.flush()

    return db_account


def get_all_accounts(session: Session) -> Sequence[Account]:
    return session.scalars(select(Account)).all()


def get_account_by_id(session: Session, account_id: UUID) -> Account:
    db_account = session.get(Account, account_id)
    if db_account is None:
        raise AccountDoesNotExistError(account_id=account_id)
    return db_account


def get_account_memberships_by_id(session: Session, account_id: UUID, current_user_id: UUID) -> Sequence[Membership]:
    db_account = session.get(Account, account_id)
    # Check if account exists
    if db_account is None:
        raise AccountDoesNotExistError(account_id=account_id)

    # Check if current user is a member of the account
    is_a_member = (
        session.scalar(
            select(1).where(Membership.account_id == account_id, Membership.user_id == current_user_id).limit(1)
        )
        is not None
    )

    if not is_a_member:
        raise UserNotMemberOfTheAccountError(user_id=current_user_id, account_id=account_id)

    account_memberships = session.scalars(select(Membership).where(Membership.account_id == account_id)).all()

    return account_memberships


def get_account_expenses_by_id(session: Session, account_id: UUID, current_user_id: UUID) -> Sequence[Expense]:
    db_account = session.get(Account, account_id)
    # Check if account exists
    if db_account is None:
        raise AccountDoesNotExistError(account_id=account_id)

    # Check if account is ACTIVE and disallow mutations when INACTIVE
    ensure_account_mutable(account_id=account_id, account_status=db_account.status, operation=Operation.EXPENSE_READ)

    # Check if current user is a member of the account
    is_a_member = (
        session.scalar(
            select(1).where(Membership.account_id == account_id, Membership.user_id == current_user_id).limit(1)
        )
        is not None
    )

    if not is_a_member:
        raise UserNotMemberOfTheAccountError(user_id=current_user_id, account_id=account_id)

    account_expenses = session.scalars(
        select(Expense).where(Expense.account_id == account_id).order_by(Expense.expense_date.desc())
    ).all()

    return account_expenses


def update_account_by_id(
    session: Session,
    account_id: UUID,
    current_user_id: UUID,
    name: str | None = None,
    status: AccountStatus | None = None,
) -> Account:
    db_account = session.get(Account, account_id)

    # Check if account exists
    if db_account is None:
        raise AccountDoesNotExistError(account_id=account_id)

    # Check if user has provided update values
    if all(value is None for value in [name, status]):
        raise AccountUpdateNoFieldsProvidedError(account_id=account_id)

    # Check if user is the OWNER of the account
    statement = (
        select(1).where(
            Membership.user_id == current_user_id,
            Membership.account_id == account_id,
            Membership.role == MembershipRole.OWNER,
        )
    ).limit(1)

    # If not OWNER raise 403
    current_user_is_owner = session.scalar(statement) is not None
    if not current_user_is_owner:
        raise AccountUpdateForbiddenError(user_id=current_user_id, account_id=account_id)

    # Apply reactivation excpetion for OWNER
    if db_account.status == AccountStatus.INACTIVE and status == AccountStatus.ACTIVE:
        ensure_inactive_account_reactivation_only(
            account_id=account_id,
            account_status=db_account.status,
            operation=Operation.ACCOUNT_UPDATE,
            other_fields_provided=(name is not None),
        )
        db_account.status = status

        session.flush()

        return db_account

    # Check if account is ACTIVE and disallow mutations when INACTIVE
    ensure_account_mutable(account_id=account_id, account_status=db_account.status, operation=Operation.ACCOUNT_UPDATE)

    if name is not None:
        db_account.name = name

    if status is not None:
        db_account.status = status

    session.flush()

    return db_account
