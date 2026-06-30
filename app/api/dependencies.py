"""Module containing db session dependencies."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import Header, HTTPException

from ..db.session import SessionLocal


def get_db():
    db = SessionLocal()
    try:
        yield db
    except:
        db.rollback()
        raise
    finally:
        db.close()


async def get_current_user_id(x_user_id: Annotated[str | None, Header()] = None) -> UUID:
    if not x_user_id:
        raise HTTPException(status_code=400, detail="X-User-Id header missing.")  # Validate UUID format
    try:
        user_uuid = UUID(x_user_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail="Invalid X-User-Id format (must be UUID)") from e
    return user_uuid
