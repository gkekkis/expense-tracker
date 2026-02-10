from __future__ import annotations

from decimal import Decimal
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..db.models.expense import Expense
from ..db.models.membership import Membership
from ..schemas.expense import ExpenseFilterParams
from ..schemas.financial_profile import BudgetStatus
from .profile_service import ProfileService


class SummaryService:
    @staticmethod
    def get_user_summary(session: Session, user_id: UUID, filters: ExpenseFilterParams) -> Decimal:
        # 1. Base query for filtered expenses
        inner_query = select(Expense.global_event_id, Expense.calculated_user_share).where(
            Expense.account_id.in_(select(Membership.account_id).where(Membership.user_id == user_id))
        )

        # Apply all existing filters to the inner query
        if filters.account_id:
            inner_query = inner_query.where(Expense.account_id == filters.account_id)
        if filters.start_date:
            inner_query = inner_query.where(Expense.expense_date >= filters.start_date)
        if filters.end_date:
            inner_query = inner_query.where(Expense.expense_date <= filters.end_date)
        if filters.category_id:
            inner_query = inner_query.where(Expense.category_id == filters.category_id)
        if filters.min_amount:
            inner_query = inner_query.where(Expense.amount >= filters.min_amount)
        if filters.max_amount:
            inner_query = inner_query.where(Expense.amount <= filters.max_amount)
        if filters.status:
            inner_query = inner_query.where(Expense.status == filters.status)

        # Text search filter
        if filters.search_query and isinstance(filters.search_query, str):
            search_input = filters.search_query.strip()
            if search_input:
                search_str = f"{search_input}:*"
                inner_query = inner_query.where(
                    func.to_tsvector("english", Expense.description).op("@@")(func.to_tsquery("english", search_str))
                )

        # 2. Optimization: Deduplication + Summation in SQL
        # We turn the filtered results into a subquery
        sub = inner_query.subquery()

        # 3. Query for distinct global event shares
        distinct_shares = (
            select(func.sum(sub.c.calculated_user_share))
            .where(sub.c.global_event_id.is_not(None))
            .group_by(sub.c.global_event_id)
        )

        # 4. Query for all unique personal shares (where global_id is null)
        personal_shares = select(func.sum(sub.c.calculated_user_share)).where(sub.c.global_event_id.is_(None))

        # 5. Combine them
        total = (session.scalar(distinct_shares) or Decimal("0.00")) + (
            session.scalar(personal_shares) or Decimal("0.00")
        )

        return total

    @staticmethod
    def get_budget_status(
        session: Session, user_id: UUID, filters: ExpenseFilterParams, account_id: UUID | None = None
    ) -> BudgetStatus:
        if account_id:
            filters.account_id = account_id

        # 1. Get the spent amount (Ensure this method uses filters.account_id in its WHERE clause)
        total_spent = SummaryService().get_user_summary(session=session, user_id=user_id, filters=filters)

        total_income = Decimal("0.00")

        # 2. Income Logic (This part looks fine for isolation)
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

        # 3. Calculations
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
