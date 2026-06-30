"""Authentication service functions."""

from __future__ import annotations

from sqlalchemy.orm import Session

from ..api.core.security import verify_password
from ..db.models.user import User
from ..domain.users.user import UserStatus
from .user_service import get_user_by_email


def authenticate_user(session: Session, email: str, password: str) -> User | None:
    user = get_user_by_email(session=session, email=email)
    if user is None:
        return None
    if user.status != UserStatus.ACTIVE:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user
