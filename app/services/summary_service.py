from __future__ import annotations

from decimal import Decimal
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..db.models.expense import Expense
from ..db.models.membership import Membership
from ..domain.expenses.expense import ExpenseStatus
from ..schemas.expense import ExpenseFilterParams
from ..schemas.financial_profile import BudgetStatus
from .profile_service import ProfileService


class SummaryService:
    @staticmethod
    def get_user_summary(session: Session, user_id: UUID, filters: ExpenseFilterParams) -> Decimal:
        stmt = select(func.sum(Expense.calculated_user_share))
        stmt = stmt.where(Expense.account_id == filters.account_id)

        if filters.status:
            stmt = stmt.where(Expense.status.in_(filters.status))
        else:
            stmt = stmt.where(Expense.status != ExpenseStatus.CANCELLED)

        if filters.start_date:
            stmt = stmt.where(Expense.expense_date >= filters.start_date)
        if filters.end_date:
            stmt = stmt.where(Expense.expense_date <= filters.end_date)
        if filters.category_id:
            stmt = stmt.where(Expense.category_id == filters.category_id)
        if filters.min_amount is not None:
            stmt = stmt.where(Expense.amount >= filters.min_amount)
        if filters.max_amount is not None:
            stmt = stmt.where(Expense.amount <= filters.max_amount)
        if filters.user_id:
            stmt = stmt.where(Expense.created_by_user_id == filters.user_id)
        if filters.search_query and isinstance(filters.search_query, str):
            search_input = filters.search_query.strip()
            if search_input:
                search_str = f"{search_input}:*"
                stmt = stmt.where(
                    func.to_tsvector("english", Expense.description).op("@@")(func.to_tsquery("english", search_str))
                )

        return session.scalar(stmt) or Decimal("0.00")

    @staticmethod
    def get_budget_status(
        session: Session, user_id: UUID, filters: ExpenseFilterParams, account_id: UUID | None = None
    ) -> BudgetStatus:
        if account_id:
            filters.account_id = account_id

        total_spent = SummaryService.get_user_summary(session=session, user_id=user_id, filters=filters)
        total_income = Decimal("0.00")

        if account_id:
            user_financial_profile = ProfileService().get_profile_by_account_id(session=session, account_id=account_id)
            if user_financial_profile:
                total_income = user_financial_profile.monthly_net_income
        else:
            membership_stmt = select(Membership.account_id).where(Membership.user_id == user_id)
            user_account_ids = session.scalars(membership_stmt).all()
            for acc_id in user_account_ids:
                user_financial_profile = ProfileService().get_profile_by_account_id(session=session, account_id=acc_id)
                if user_financial_profile:
                    total_income += user_financial_profile.monthly_net_income

        remaining_budget = total_income - total_spent
        health_percentage = 0.0
        if total_income > 0:
            health_percentage = float((remaining_budget / total_income) * 100)

        return BudgetStatus(
            total_income=total_income,
            total_spent=total_spent,
            remaining_budget=remaining_budget,
            health_percentage=health_percentage,
        )
