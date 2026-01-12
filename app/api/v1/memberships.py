from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from ...schemas.membership import MembershipCreate, MembershipRead, MembershipUpdate
from ...services.membership_service import (
    create_membership,
    delete_membership_by_id,
    get_all_memberships,
    get_membership_by_id,
    update_membership_by_id,
)
from ..dependencies import get_current_user_id, get_db

router = APIRouter(prefix="/memberships", tags=["memberships"])

CurrentUser = Annotated[UUID, Depends(get_current_user_id)]
Db = Annotated[Session, Depends(get_db)]


@router.post("/", response_model=MembershipRead)
def create_membership_endpoint(membership_in: MembershipCreate, current_user_id: CurrentUser, db: Db) -> MembershipRead:
    db_membership = create_membership(session=db, membership=membership_in, current_user_id=current_user_id)
    db.commit()
    db.refresh(db_membership)
    return db_membership


@router.get("/", response_model=list[MembershipRead])
def get_all_memberships_endpoint(db: Db) -> list[MembershipRead]:
    db_memberships = get_all_memberships(session=db)
    return db_memberships


@router.get("/{membership_id}", response_model=MembershipRead)
def get_memberhsip_by_id_endpoint(membership_id: UUID, db: Db) -> MembershipRead:
    db_membership = get_membership_by_id(session=db, membership_id=membership_id)
    return db_membership


@router.patch("/{membership_id}", response_model=MembershipRead)
def update_membership_by_id_endpoint(
    membership_id: UUID, membership_update: MembershipUpdate, current_user_id: CurrentUser, db: Db
) -> MembershipRead:
    updated_membership = update_membership_by_id(
        session=db, membership_id=membership_id, current_user_id=current_user_id, role=membership_update.role
    )

    db.commit()
    db.refresh(updated_membership)

    return updated_membership


@router.delete("/{membership_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_membership_by_id_endpoint(membership_id: UUID, current_user_id: CurrentUser, db: Db) -> None:
    delete_membership_by_id(session=db, membership_id=membership_id, current_user_id=current_user_id)
    db.commit()
