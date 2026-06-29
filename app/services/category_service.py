"""Category service.

Currently the UI mainly needs a read-only list of categories per account so it can:
- populate dropdowns for expense create/edit
- render category name/emoji instead of only category_id
"""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db.models.account import Account
from ..db.models.category import Category
from ..db.models.membership import Membership
from ..errors.errors import AccountDoesNotExistError, UserNotMemberOfTheAccountError


def get_categories_by_account(session: Session, account_id: UUID, current_user_id: UUID) -> list[Category]:
    db_account = session.get(Account, account_id)
    if not db_account:
        raise AccountDoesNotExistError(account_id=account_id)

    membership_exists = session.scalar(
        select(1).where(Membership.account_id == account_id, Membership.user_id == current_user_id).limit(1)
    )
    if not membership_exists:
        raise UserNotMemberOfTheAccountError(user_id=current_user_id, account_id=account_id)

    query = select(Category).where(Category.account_id == account_id).order_by(Category.name.asc())
    return list(session.scalars(query).all())
