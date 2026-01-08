from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from ...schemas.expense import ExpenseCreate, ExpenseRead, ExpenseUpdate
from ...services.expense_service import (
    create_expense,
    delete_expense_by_id,
    get_all_expenses,
    get_expense_by_id,
    update_expense_by_id,
)
from ..dependencies import get_db

router = APIRouter(prefix="/expenses", tags=["expenses"])


@router.post("/", response_model=ExpenseRead)
def create_expense_endpoint(
    expense_in: ExpenseCreate, created_by_user_id: UUID | None = None, db: Session = Depends(get_db)
) -> ExpenseRead:
    db_expense = create_expense(session=db, expense_in=expense_in, created_by_user_id=created_by_user_id)
    db.commit()
    db.refresh(db_expense)
    return db_expense


@router.get("/", response_model=list[ExpenseRead])
def get_all_expenses_endpoint(db: Session = Depends(get_db)) -> list[ExpenseRead]:
    db_expenses = get_all_expenses(session=db)
    return db_expenses


@router.get("/{expense_id}", response_model=ExpenseRead)
def get_expense_by_id_endpoint(expense_id: UUID, db: Session = Depends(get_db)) -> ExpenseRead:
    db_expense = get_expense_by_id(session=db, expense_id=expense_id)
    return db_expense


@router.patch("/{expense_id}", response_model=ExpenseRead)
def update_expense_by_id_endpoint(
    expense_id: UUID, expense_update: ExpenseUpdate, current_user_id: UUID, db: Session = Depends(get_db)
) -> ExpenseRead:
    updated_expense = update_expense_by_id(
        session=db,
        expense_id=expense_id,
        current_user_id=current_user_id,
        description=expense_update.description,
        amount=expense_update.amount,
        category=expense_update.category,
        expense_date=expense_update.expense_date,
    )

    db.commit()
    db.refresh(updated_expense)

    return updated_expense


@router.delete("/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_expense_by_id_endpoint(expense_id: UUID, current_user_id: UUID, db: Session = Depends(get_db)) -> None:
    delete_expense_by_id(session=db, expense_id=expense_id, current_user_id=current_user_id)
    db.commit()
