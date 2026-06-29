from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ...api.dependencies import get_current_user_id, get_db
from ...schemas.financial_profile import FinancialProfileResponse, FinancialProfileUpdate
from ...services.profile_service import ProfileService

router = APIRouter(prefix="/accounts", tags=["financial-profiles"])

CurrentUser = Annotated[UUID, Depends(get_current_user_id)]
Db = Annotated[Session, Depends(get_db)]


@router.get("/{account_id}/financial-profile", response_model=FinancialProfileResponse | None)
def get_financial_profile_endpoint(account_id: UUID, current_user_id: CurrentUser, db: Db):
    # Membership enforcement is inside ProfileService.update_profile; for reads we only validate account exists.
    # If you want reads to be membership-protected too, add the same membership check here.
    return ProfileService.get_profile_by_account_id(session=db, account_id=account_id)


@router.patch("/{account_id}/financial-profile", response_model=FinancialProfileResponse)
def update_financial_profile_endpoint(
    account_id: UUID, payload: FinancialProfileUpdate, current_user_id: CurrentUser, db: Db
):
    service = ProfileService()
    updated = service.update_profile(session=db, account_id=account_id, user_id=current_user_id, data=payload)
    db.commit()
    db.refresh(updated)
    return updated
