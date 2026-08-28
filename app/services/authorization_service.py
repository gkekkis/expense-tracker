"""Reusable account authorization helpers."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db.models.account import Account
from ..db.models.membership import Membership
from ..domain.memberships.membership import MembershipRole
from ..errors.errors import AccountDoesNotExistError, AccountMutationForbiddenError, UserNotMemberOfTheAccountError


@dataclass(frozen=True)
class AccountAccess:
    account: Account
    membership: Membership


def require_account_member(session: Session, account_id: UUID, user_id: UUID) -> AccountAccess:
    """Return account access details or raise when the user cannot read the account."""
    account = session.get(Account, account_id)
    if account is None:
        raise AccountDoesNotExistError(account_id=account_id)

    membership = session.execute(
        select(Membership).where(Membership.account_id == account_id, Membership.user_id == user_id)
    ).scalar_one_or_none()
    if membership is None:
        raise UserNotMemberOfTheAccountError(user_id=user_id, account_id=account_id)

    return AccountAccess(account=account, membership=membership)


def require_account_writer(session: Session, account_id: UUID, user_id: UUID) -> AccountAccess:
    """Return account access details or raise when the user's role is read-only."""
    access = require_account_member(session=session, account_id=account_id, user_id=user_id)
    if access.membership.role == MembershipRole.VIEWER:
        raise AccountMutationForbiddenError(user_id=user_id, account_id=account_id)
    return access


def get_account_ids_for_user(session: Session, user_id: UUID) -> list[UUID]:
    """Return account ids where the user has a membership."""
    return list(session.scalars(select(Membership.account_id).where(Membership.user_id == user_id)).all())
