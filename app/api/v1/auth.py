"""Authentication API endpoints."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ...api.core.security import TOKEN_TYPE, create_access_token
from ...api.dependencies import get_current_user_id, get_db
from ...schemas.auth import LoginRequest, TokenResponse
from ...schemas.user import UserRead
from ...services.auth_service import authenticate_user
from ...services.user_service import get_user_by_id

router = APIRouter(prefix="/auth", tags=["auth"])

CurrentUser = Annotated[UUID, Depends(get_current_user_id)]
Db = Annotated[Session, Depends(get_db)]


@router.post("/login", response_model=TokenResponse)
def login_endpoint(payload: LoginRequest, db: Db) -> TokenResponse:
    user = authenticate_user(session=db, email=str(payload.email), password=payload.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    expires_in = 86400
    token = create_access_token(user_id=user.id, expires_in_seconds=expires_in)
    return TokenResponse(access_token=token, token_type=TOKEN_TYPE, expires_in=expires_in)


@router.get("/me", response_model=UserRead)
def current_user_endpoint(current_user_id: CurrentUser, db: Db) -> UserRead:
    return get_user_by_id(session=db, user_id=current_user_id)
