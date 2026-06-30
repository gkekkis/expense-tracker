from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from pydantic import EmailStr
from sqlalchemy.orm import Session

from ...errors.errors import UserListForbiddenError, UserReadForbiddenError
from ...schemas.account import AccountRead
from ...schemas.user import UserCreate, UserRead
from ...services.user_service import (
    create_user,
    get_accounts_by_id,
    get_all_users,
    get_user_by_id,
    search_users_by_exact_email,
)
from ..dependencies import allow_local_prototype_features, get_current_user_id, get_db

router = APIRouter(prefix="/users", tags=["users"])

CurrentUser = Annotated[UUID, Depends(get_current_user_id)]
Db = Annotated[Session, Depends(get_db)]


@router.post("/", response_model=UserRead)
def create_user_endpoint(user_in: UserCreate, db: Db) -> UserRead:
    db_user = create_user(session=db, user_in=user_in)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.get("/", response_model=list[UserRead])
def get_all_users_endpoint(db: Db) -> list[UserRead]:
    if not allow_local_prototype_features():
        raise UserListForbiddenError
    db_users = get_all_users(session=db)
    return list(db_users)


@router.get("/me/accounts", response_model=list[AccountRead])
def get_accounts_by_id_endpoint(current_user_id: CurrentUser, db: Db) -> list[AccountRead]:
    return list(get_accounts_by_id(session=db, current_user_id=current_user_id))


@router.get("/search", response_model=list[UserRead])
def search_users_endpoint(
    current_user_id: CurrentUser, db: Db, email: Annotated[EmailStr, Query(...)]
) -> list[UserRead]:
    return search_users_by_exact_email(session=db, email=str(email))


@router.get("/{user_id}", response_model=UserRead)
def get_user_by_id_endpoint(user_id: UUID, current_user_id: CurrentUser, db: Db) -> UserRead:
    if user_id != current_user_id:
        raise UserReadForbiddenError(user_id=current_user_id, target_user_id=user_id)
    return get_user_by_id(session=db, user_id=user_id)
