from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ...schemas.user import UserCreate, UserRead
from ...services.user_service import create_user, get_all_users, get_user_by_id
from ..dependencies import get_db

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserRead)
def create_user_endpoint(user_in: UserCreate, db: Session = Depends(get_db)) -> UserRead:
    db_user = create_user(session=db, user_in=user_in)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.get("/", response_model=list[UserRead])
def get_all_users_endpoint(db: Session = Depends(get_db)) -> list[UserRead]:
    db_users = get_all_users(session=db)
    return db_users


@router.get("/{user_id}", response_model=UserRead)
def get_user_by_id_endpoint(user_id: UUID, db: Session = Depends(get_db)) -> UserRead:
    db_user = get_user_by_id(session=db, user_id=user_id)
    return db_user
