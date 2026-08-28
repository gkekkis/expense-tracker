"""Module containing User session functionalities."""

from __future__ import annotations

import logging
from typing import Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from ...db.models.account import Account
from ...db.models.category import Category
from ...db.models.expense import Expense
from ...db.models.membership import Membership, MembershipRole
from ...domain.accounts.account import AccountStatus
from ...domain.expenses.category_defaults import CATEGORY_EMOJI_MAP
from ...domain.expenses.expense import ExpenseCategory
from ...domain.operations import Operation
from ...domain.policies.account_state import ensure_account_mutable, ensure_inactive_account_reactivation_only
from ...errors.errors import AccountDoesNotExistError, AccountUpdateForbiddenError, AccountUpdateNoFieldsProvidedError
from ...schemas.account import AccountCreate
from ..audit_log_service import account_snapshot, membership_snapshot, record_audit_log
from ..authorization_service import require_account_member
from .onboarding import process_new_account_onboarding

logger = logging.getLogger(__name__)


def create_account(session: Session, account_in: AccountCreate, current_user_id: UUID) -> Account:
    db_account = Account(name=account_in.name, status=account_in.status, default_category_id=None)

    session.add(db_account)
    session.flush()

    category_ids = seed_default_categories(session=session, account_id=db_account.id)
    db_account.default_category_id = category_ids[ExpenseCategory.MISC]

    owner_membership = Membership(user_id=current_user_id, account_id=db_account.id, role=MembershipRole.OWNER)
    session.add(owner_membership)

    db_account = process_new_account_onboarding(session=session, account=db_account, category_ids=category_ids)
    session.flush()

    record_audit_log(
        session=session,
        actor_user_id=current_user_id,
        account_id=db_account.id,
        action="account.created",
        entity_type="account",
        entity_id=db_account.id,
        after=account_snapshot(db_account),
    )
    record_audit_log(
        session=session,
        actor_user_id=current_user_id,
        account_id=db_account.id,
        action="membership.created",
        entity_type="membership",
        entity_id=owner_membership.id,
        after=membership_snapshot(owner_membership),
    )

    return db_account


def get_all_accounts(session: Session, current_user_id: UUID) -> Sequence[Account]:
    return session.scalars(
        select(Account)
        .join(Membership, Membership.account_id == Account.id)
        .where(Membership.user_id == current_user_id)
        .order_by(Account.created_at.desc())
    ).all()


def get_account_by_id(session: Session, account_id: UUID, current_user_id: UUID) -> Account:
    return require_account_member(session=session, account_id=account_id, user_id=current_user_id).account


def get_account_memberships_by_id(session: Session, account_id: UUID, current_user_id: UUID) -> Sequence[Membership]:
    require_account_member(session=session, account_id=account_id, user_id=current_user_id)

    account_memberships = session.scalars(select(Membership).where(Membership.account_id == account_id)).all()

    return account_memberships


def get_account_expenses_by_id(session: Session, account_id: UUID, current_user_id: UUID) -> Sequence[Expense]:
    access = require_account_member(session=session, account_id=account_id, user_id=current_user_id)
    db_account = access.account

    # Check if account is ACTIVE and disallow mutations when INACTIVE
    ensure_account_mutable(account_id=account_id, account_status=db_account.status, operation=Operation.EXPENSE_READ)

    account_expenses = session.scalars(
        select(Expense)
        .options(selectinload(Expense.category))
        .where(Expense.account_id == account_id)
        .order_by(Expense.expense_date.desc())
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

    access = require_account_member(session=session, account_id=account_id, user_id=current_user_id)
    if access.membership.role != MembershipRole.OWNER:
        raise AccountUpdateForbiddenError(user_id=current_user_id, account_id=account_id)

    before = account_snapshot(db_account)

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
        record_audit_log(
            session=session,
            actor_user_id=current_user_id,
            account_id=account_id,
            action="account.updated",
            entity_type="account",
            entity_id=account_id,
            before=before,
            after=account_snapshot(db_account),
        )

        return db_account

    # Check if account is ACTIVE and disallow mutations when INACTIVE
    ensure_account_mutable(account_id=account_id, account_status=db_account.status, operation=Operation.ACCOUNT_UPDATE)

    if name is not None:
        db_account.name = name

    if status is not None:
        db_account.status = status

    session.flush()
    record_audit_log(
        session=session,
        actor_user_id=current_user_id,
        account_id=account_id,
        action="account.updated",
        entity_type="account",
        entity_id=account_id,
        before=before,
        after=account_snapshot(db_account),
    )

    return db_account


def seed_default_categories(session: Session, account_id: UUID) -> dict[ExpenseCategory, UUID]:
    category_ids: dict[ExpenseCategory, UUID] = {}
    for exp_category in ExpenseCategory:
        exp_emoji = CATEGORY_EMOJI_MAP[exp_category]
        db_category = Category(account_id=account_id, name=exp_category.value, emoji=exp_emoji)
        session.add(db_category)
        session.flush()
        category_ids[exp_category] = db_category.id

    return category_ids
