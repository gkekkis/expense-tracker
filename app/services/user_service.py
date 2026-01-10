"""Module containign User session functionalities."""

from __future__ import annotations

from typing import Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session  # noqa: TCH002

from ..db.models.account import Account
from ..db.models.membership import Membership
from ..db.models.user import User
from ..errors.errors import UserDoesNotExistError, UserHasNoAccountsError
from ..schemas.user import UserCreate  # noqa: TCH001


def create_user(session: Session, user_in: UserCreate) -> User:
    db_user = User(name=user_in.name, email=user_in.email, status=user_in.status)

    session.add(db_user)
    session.flush()

    return db_user


def get_all_users(session: Session) -> Sequence[User]:
    return session.scalars(select(User)).all()


def get_user_by_id(session: Session, user_id: UUID) -> User:
    db_user = session.get(User, user_id)
    if db_user is None:
        raise UserDoesNotExistError(user_id=user_id)
    return db_user


def get_accounts_by_id(session: Session, current_user_id: UUID) -> Sequence[Account]:
    # Get all current user accounts

    current_user_accounts = session.scalars(
        select(Account).join(Membership).where(Membership.id == current_user_id)
    ).all()

    if current_user_accounts is None or not len(current_user_accounts):
        raise UserHasNoAccountsError(user_id=current_user_id)

    return current_user_accounts
