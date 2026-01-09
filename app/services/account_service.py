"""Module containing User session functionalities."""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

from typing import Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session  # noqa: TCH002

from ..db.models.account import Account
from ..db.models.membership import Membership, MembershipRole
from ..domain.accounts.account import AccountStatus
from ..domain.operations import Operation
from ..domain.policies.account_state import ensure_account_mutable, ensure_inactive_account_reactivation_only
from ..errors.errors import (
    AccountDoesNotExistError,
    AccountUpdateForbiddenError,
    AccountUpdateNoFieldsProvidedError,
    UserNotMemberOfTheAccountError,
)
from ..schemas.account import AccountCreate  # noqa: TCH001


def create_account(session: Session, account_in: AccountCreate, current_user_id: UUID) -> Account:
    db_account = Account(name=account_in.name, status=AccountStatus.ACTIVE)

    session.add(db_account)
    session.flush()

    # Check if membership exists
    membership_exists = (
        session.scalar(
            select(1).where(Membership.account_id == db_account.id, Membership.user_id == current_user_id).limit(1)
        )
        is not None
    )

    if not membership_exists:
        db_membership = Membership(user_id=current_user_id, account_id=db_account.id, role=MembershipRole.OWNER)
        session.add(db_membership)
        session.flush()

    return db_account


def get_all_accounts_for_user(session: Session, current_user_id: UUID) -> Sequence[Account]:
    accounts = session.query(Account).join(Membership).filter(Membership.user_id == current_user_id).all()
    return accounts


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
