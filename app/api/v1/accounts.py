from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ...schemas.account import AccountCreate, AccountRead, AccountUpdate
from ...schemas.expense import ExpenseRead
from ...schemas.membership import MembershipRead
from ...services.account_service import (
    create_account,
    get_account_by_id,
    get_account_expenses_by_id,
    get_account_memberships_by_id,
    get_all_accounts,
    update_account_by_id,
)
from ..dependencies import get_current_user_id, get_db

router = APIRouter(prefix="/accounts", tags=["accounts"])


CurrentUser = Annotated[UUID, Depends(get_current_user_id)]
Db = Annotated[Session, Depends(get_db)]


@router.post("/", response_model=AccountRead)
def create_account_endpoint(account_in: AccountCreate, db: Db) -> AccountRead:
    db_account = create_account(session=db, account_in=account_in)
    db.commit()
    db.refresh(db_account)
    return db_account


@router.get("/", response_model=list[AccountRead])
def get_all_accounts_endpoint(db: Db) -> list[AccountRead]:
    db_accounts = get_all_accounts(session=db)
    return db_accounts


@router.get("/{account_id}", response_model=AccountRead)
def get_account_by_id_endpoint(account_id: UUID, db: Db) -> AccountRead:
    db_account = get_account_by_id(session=db, account_id=account_id)
    return db_account


@router.get("/{account_id}/memberships", response_model=list[MembershipRead])
def get_account_memberships_by_id_endpoint(
    account_id: UUID, current_user_id: CurrentUser, db: Db
) -> list[MembershipRead]:
    all_account_memberships = get_account_memberships_by_id(
        session=db, account_id=account_id, current_user_id=current_user_id
    )

    return all_account_memberships


@router.get("/{account_id}/expenses", response_model=list[ExpenseRead])
def get_account_expenses_by_id_endpoint(account_id: UUID, current_user_id: CurrentUser, db: Db) -> list[ExpenseRead]:
    all_account_expenses = get_account_expenses_by_id(
        session=db, account_id=account_id, current_user_id=current_user_id
    )

    return all_account_expenses


@router.patch("/{account_id}", response_model=AccountRead)
def update_account_by_id_endpoint(
    account_id: UUID, account_update: AccountUpdate, current_user_id: CurrentUser, db: Db
) -> AccountRead:
    updated_account = update_account_by_id(
        session=db,
        account_id=account_id,
        current_user_id=current_user_id,
        name=account_update.name,
        status=account_update.status,
    )

    db.commit()
    db.refresh(updated_account)

    return updated_account
