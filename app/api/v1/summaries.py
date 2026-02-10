from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ...schemas.expense import ExpenseFilterParams
from ...schemas.financial_profile import BudgetStatus
from ...services.summary_service import SummaryService
from ..dependencies import get_current_user_id, get_db

router = APIRouter(prefix="/summaries", tags=["summaries"])

CurrentUser = Annotated[UUID, Depends(get_current_user_id)]
Db = Annotated[Session, Depends(get_db)]


@router.get("/budget-status", response_model=BudgetStatus)
def get_budget_status_endpoint(
    filters: Annotated[ExpenseFilterParams, Depends()],
    current_user_id: CurrentUser,
    db: Db,
    account_id: UUID | None = None,
) -> BudgetStatus:
    """
    Returns the high-level financial health status,
    accounting for deduplicated shared expenses.
    """
    return SummaryService.get_budget_status(session=db, user_id=current_user_id, filters=filters, account_id=account_id)
