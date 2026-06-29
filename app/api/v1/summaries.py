from __future__ import annotations

from datetime import date
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ...db.models.expense import ExpenseStatus
from ...schemas.expense import ExpenseFilterParams
from ...schemas.financial_profile import BudgetStatus
from ...services.summary_service import SummaryService
from ..dependencies import get_current_user_id, get_db

router = APIRouter(prefix="/summaries", tags=["summaries"])

CurrentUser = Annotated[UUID, Depends(get_current_user_id)]
Db = Annotated[Session, Depends(get_db)]


@router.get("/budget-status", response_model=BudgetStatus)
def get_budget_status_endpoint(
    # 1. Explicitly pull status as a list using Query
    account_id: UUID,
    current_user_id: CurrentUser,
    db: Db,
    status: list[ExpenseStatus] | None = Query(None),
    start_date: date | None = None,
    end_date: date | None = None,
    category_id: UUID | None = None,
    min_amount: float | None = None,
    max_amount: float | None = None,
    search_query: str | None = None,
    user_id: UUID | None = None,
) -> BudgetStatus:
    # 2. Re-assemble the filters object to pass to the service
    filters = ExpenseFilterParams(
        account_id=account_id,
        status=status,
        start_date=start_date,
        end_date=end_date,
        category_id=category_id,
        min_amount=min_amount,
        max_amount=max_amount,
        search_query=search_query,
        user_id=user_id,
    )

    return SummaryService.get_budget_status(session=db, user_id=current_user_id, filters=filters, account_id=account_id)
