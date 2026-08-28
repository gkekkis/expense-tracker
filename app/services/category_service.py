"""Category service.

Currently the UI mainly needs a read-only list of categories per account so it can:
- populate dropdowns for expense create/edit
- render category name/emoji instead of only category_id
"""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db.models.category import Category
from .authorization_service import require_account_member


def get_categories_by_account(session: Session, account_id: UUID, current_user_id: UUID) -> list[Category]:
    require_account_member(session=session, account_id=account_id, user_id=current_user_id)

    query = select(Category).where(Category.account_id == account_id).order_by(Category.name.asc())
    return list(session.scalars(query).all())
