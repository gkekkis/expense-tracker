"""Module containign User session functionalities."""

from __future__ import annotations

from typing import Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session  # noqa: TCH002

from ..api.core.security import hash_password
from ..db.models.account import Account
from ..db.models.membership import Membership
from ..db.models.user import User
from ..errors.errors import UserDoesNotExistError, UserHasNoAccountsError
from ..schemas.user import UserCreate  # noqa: TCH001


def create_user(session: Session, user_in: UserCreate) -> User:
    password_hash = hash_password(user_in.password) if user_in.password else None
    db_user = User(name=user_in.name, email=user_in.email, status=user_in.status, password_hash=password_hash)

    session.add(db_user)
    session.flush()

    return db_user


def get_all_users(session: Session) -> Sequence[User]:
    return session.scalars(select(User)).all()


def search_users_by_exact_email(session: Session, email: str) -> list[User]:
    db_user = get_user_by_email(session=session, email=email)
    return [db_user] if db_user else []


def get_user_by_id(session: Session, user_id: UUID) -> User:
    db_user = session.get(User, user_id)
    if db_user is None:
        raise UserDoesNotExistError(user_id=user_id)
    return db_user


def get_user_by_email(session: Session, email: str) -> User | None:
    return session.scalars(select(User).where(User.email == email)).first()


def get_accounts_by_id(session: Session, current_user_id: UUID) -> Sequence[Account]:
    # Check if user exists
    db_user = session.get(User, current_user_id)
    if db_user is None:
        raise UserDoesNotExistError(user_id=current_user_id)

    # Get all current user accounts
    current_user_accounts = session.scalars(
        select(Account).join(Membership).where(Membership.user_id == current_user_id)
    ).all()

    if current_user_accounts is None or not len(current_user_accounts):
        raise UserHasNoAccountsError(user_id=current_user_id)

    return current_user_accounts
