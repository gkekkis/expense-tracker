"""Module containign User session functionalities."""

from __future__ import annotations

from typing import Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session  # noqa: TCH002

from ..db.models.user import User
from ..errors.errors import UserDoesNotExistError
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
