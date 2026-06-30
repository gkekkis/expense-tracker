"""Module containing db session dependencies."""

from __future__ import annotations

import os
from typing import Annotated
from uuid import UUID

from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from ..db.session import SessionLocal
from .core.security import AuthTokenError, verify_access_token

bearer_scheme = HTTPBearer(auto_error=False)


def get_db():
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def _allow_dev_user_header() -> bool:
    return (
        os.getenv("ALLOW_X_USER_ID_AUTH", "False").lower() == "true"
        or os.getenv("DEV", "False").lower() == "true"
        or os.getenv("TESTING", "False").lower() == "true"
    )


async def get_current_user_id(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)] = None,
    x_user_id: Annotated[str | None, Header()] = None,
) -> UUID:
    if credentials:
        try:
            return verify_access_token(credentials.credentials)
        except AuthTokenError as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired bearer token.",
                headers={"WWW-Authenticate": "Bearer"},
            ) from exc

    if not x_user_id or not _allow_dev_user_header():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Bearer token missing.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        return UUID(x_user_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail="Invalid X-User-Id format (must be UUID)") from e
