from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, Query, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from ...db.models.currency import CurrencyRate
from ...domain.currencies.currency import Currency
from ...schemas.expense import (
    ExpenseCreate,
    ExpenseFilterParams,
    ExpenseRead,
    ExpenseStatus,
    ExpenseUpdate,
    PaginatedExpenseResponse,
)
from ...services.currency_service import CurrencyService
from ...services.expense_service import (
    confirm_pending_expense,
    create_expense,
    delete_expense_by_id,
    get_all_expenses,
    get_expense_by_id,
    get_filtered_expenses,
    update_expense_by_id,
)
from ...utils.formatters import format_currency
from ..dependencies import get_current_user_id, get_db

router = APIRouter(prefix="/expenses", tags=["expenses"])

CurrentUser = Annotated[UUID, Depends(get_current_user_id)]
Db = Annotated[Session, Depends(get_db)]


@router.post("/", response_model=ExpenseRead)
def create_expense_endpoint(expense_in: ExpenseCreate, db: Db, created_by_user_id: CurrentUser) -> ExpenseRead:
    db_expense = create_expense(session=db, expense_in=expense_in, created_by_user_id=created_by_user_id)
    db.commit()
    db.refresh(db_expense)
    return db_expense


@router.get("/", response_model=list[ExpenseRead])
def get_all_expenses_endpoint(current_user_id: CurrentUser, db: Db) -> list[ExpenseRead]:
    db_expenses = get_all_expenses(session=db, current_user_id=current_user_id)
    return db_expenses


@router.get("/{expense_id}", response_model=ExpenseRead)
def get_expense_by_id_endpoint(expense_id: UUID, current_user_id: CurrentUser, db: Db) -> ExpenseRead:
    db_expense = get_expense_by_id(session=db, expense_id=expense_id, current_user_id=current_user_id)
    return db_expense


@router.patch("/{expense_id}", response_model=ExpenseRead)
def update_expense_by_id_endpoint(
    expense_id: UUID, expense_update: ExpenseUpdate, current_user_id: CurrentUser, db: Db
) -> ExpenseRead:
    updated_expense = update_expense_by_id(
        session=db,
        expense_id=expense_id,
        current_user_id=current_user_id,
        description=expense_update.description,
        amount=expense_update.amount,
        category_id=expense_update.category_id,
        expense_date=expense_update.expense_date,
    )

    db.commit()
    db.refresh(updated_expense)

    return updated_expense


@router.delete("/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_expense_by_id_endpoint(expense_id: UUID, current_user_id: CurrentUser, db: Db) -> None:
    delete_expense_by_id(session=db, expense_id=expense_id, current_user_id=current_user_id)
    db.commit()


@router.post("/search", response_model=PaginatedExpenseResponse)
async def get_filtered_expenses_endpoint(
    expense_filters: ExpenseFilterParams,
    current_user_id: CurrentUser,
    db: Db,
    background_tasks: BackgroundTasks,
    target_currency: Currency | None = Query(None),
    curr_service: CurrencyService = Depends(CurrencyService),
) -> PaginatedExpenseResponse:
    # 1. Fetch raw items
    items, total_count, all_matching = get_filtered_expenses(
        session=db, params=expense_filters, current_user_id=current_user_id
    )

    # 2. Use EUR as fallback
    calc_currency = target_currency or Currency.EUR

    # 3. Check if cache is stale and refresh in background
    # This prevents the current request from slowing down
    background_tasks.add_task(curr_service.refresh_cache_if_stale, db)

    # 4. Perform math
    normalized_total = await curr_service.get_normalized_total(
        db=db, expenses=all_matching, target_currency=calc_currency
    )

    # Get the timestamp to show the user how fresh the data is
    latest_rate_update = db.query(func.max(CurrencyRate.updated_at)).scalar()

    return PaginatedExpenseResponse(
        items=items,
        total_amount=normalized_total,
        total_count=total_count,
        limit=expense_filters.limit,
        offset=expense_filters.offset,
        total_amount_formatted=format_currency(amount=normalized_total, currency_code=calc_currency.value),
        rates_updated_at=latest_rate_update,
        base_currency=calc_currency.value,
    )


@router.patch("/{expense_id}/approve", response_model=ExpenseRead)
def confirm_pending_expense_endpoint(expense_id: UUID, current_user_id: CurrentUser, db: Db) -> ExpenseRead:
    # Service should return the updated object
    updated_expense = confirm_pending_expense(session=db, expense_id=expense_id, current_user_id=current_user_id)
    db.commit()
    db.refresh(updated_expense)
    return updated_expense


@router.get("/accounts/{account_id}/expenses", response_model=list[ExpenseRead])
def get_account_expenses_with_filters(
    account_id: UUID,
    current_user_id: CurrentUser,
    db: Db,
    status: ExpenseStatus | None = Query(None),  # Allows ?status=PENDING
) -> list[ExpenseRead]:
    # Build the params object manually or pass directly to a service
    params = ExpenseFilterParams(account_id=account_id, status=[status] if status else None)

    items, _, _ = get_filtered_expenses(session=db, params=params, current_user_id=current_user_id)

    return items
