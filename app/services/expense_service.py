"""Module containign User session functionalities."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Sequence
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload  # noqa: TCH002

from ..db.models.account import Account
from ..db.models.category import Category
from ..db.models.expense import Expense, ExpenseStatus
from ..db.models.recurring_template import RecurringTemplate
from ..domain.currencies.currency import Currency
from ..domain.memberships.membership import MembershipRole
from ..domain.operations import Operation
from ..domain.policies.account_state import ensure_account_mutable
from ..errors.errors import (
    AccountDoesNotExistError,
    CategoryNotFoundError,
    ExpenseDeleteForbiddenError,
    ExpenseDoesNotExistError,
    ExpenseUpdateForbiddenError,
    ExpenseUpdateNoFieldsProvidedError,
)
from ..schemas.expense import (
    ExpenseCreate,  # noqa: TCH001
    ExpenseFilterParams,
)
from .accounts.account_service import get_account_by_id
from .audit_log_service import expense_snapshot, record_audit_log
from .authorization_service import get_account_ids_for_user, require_account_member, require_account_writer
from .responsibility_service import ResponsibilityService


def create_expense(session: Session, expense_in: ExpenseCreate, created_by_user_id: UUID | None) -> Expense:
    if created_by_user_id:
        require_account_writer(session=session, account_id=expense_in.account_id, user_id=created_by_user_id)
    else:
        statement = select(1).where(Account.id == expense_in.account_id).limit(1)
        if session.scalar(statement) is None:
            raise AccountDoesNotExistError(account_id=expense_in.account_id)

    category = session.get(Category, expense_in.category_id)
    if not category or category.account_id != expense_in.account_id:
        raise CategoryNotFoundError(category_id=expense_in.category_id)

    calculated_user_share = ResponsibilityService().calculate_user_share(
        session=session,
        user_id=created_by_user_id,
        account_id=expense_in.account_id,
        total_amount=expense_in.amount,
        personal_responsibility_factor=expense_in.personal_responsibility_factor,
    )

    db_expense = Expense(
        account_id=expense_in.account_id,
        created_by_user_id=created_by_user_id,
        description=expense_in.description,
        amount=expense_in.amount,
        category_id=expense_in.category_id,
        status=expense_in.status,
        expense_date=expense_in.expense_date,
        currency=expense_in.currency,
        global_event_id=expense_in.global_event_id,
        personal_responsibility_factor=expense_in.personal_responsibility_factor,
        calculated_user_share=calculated_user_share,
    )

    session.add(db_expense)
    session.flush()
    record_audit_log(
        session=session,
        actor_user_id=created_by_user_id,
        account_id=db_expense.account_id,
        action="expense.created",
        entity_type="expense",
        entity_id=db_expense.id,
        after=expense_snapshot(db_expense),
    )
    return db_expense


def get_all_expenses(session: Session, current_user_id: UUID) -> Sequence[Expense]:
    user_account_ids = get_account_ids_for_user(session=session, user_id=current_user_id)
    if not user_account_ids:
        return []
    return session.scalars(
        select(Expense)
        .options(selectinload(Expense.category))
        .where(Expense.account_id.in_(user_account_ids))
        .order_by(Expense.expense_date.desc())
    ).all()


def get_expense_by_id(session: Session, expense_id: UUID, current_user_id: UUID) -> Expense:
    # Ensure category is available for read models
    db_expense = session.execute(
        select(Expense).options(selectinload(Expense.category)).where(Expense.id == expense_id)
    ).scalar_one_or_none()
    if db_expense is None:
        raise ExpenseDoesNotExistError(expense_id=expense_id)
    require_account_member(session=session, account_id=db_expense.account_id, user_id=current_user_id)
    return db_expense


def update_expense_by_id(
    session: Session,
    expense_id: UUID,
    current_user_id: UUID,
    description: str | None = None,
    amount: Decimal | None = None,
    category_id: UUID | None = None,  # Change 1: Use UUID
    expense_date: date | None = None,
    currency: Currency | None = None,
) -> Expense:
    db_expense = session.get(Expense, expense_id)
    if db_expense is None:
        raise ExpenseDoesNotExistError(expense_id=expense_id)

    # Check Account Status & Existence
    account_id = db_expense.account_id
    account = session.get(Account, account_id)
    if account is None:
        raise AccountDoesNotExistError(account_id=account_id)

    ensure_account_mutable(account_id=account_id, account_status=account.status, operation=Operation.EXPENSE_UPDATE)

    # Permission Check: Is user a member? Is user Owner or Creator?
    # (Keeping your existing logic here, but cleaned up slightly)
    access = require_account_writer(session=session, account_id=account_id, user_id=current_user_id)
    membership = access.membership

    is_owner = membership.role == MembershipRole.OWNER
    is_creator = db_expense.created_by_user_id == current_user_id

    if not (is_owner or is_creator):
        raise ExpenseUpdateForbiddenError(user_id=current_user_id, expense_id=expense_id, account_id=account_id)

    # Check if we actually have something to update
    if all(v is None for v in [description, amount, category_id, expense_date, currency]):
        raise ExpenseUpdateNoFieldsProvidedError(expense_id=expense_id)

    before = expense_snapshot(db_expense)

    if category_id is not None:
        category = session.get(Category, category_id)
        if not category or category.account_id != account_id:
            raise CategoryNotFoundError(category_id=category_id)
        db_expense.category_id = category_id

    # Update other fields
    if description is not None:
        db_expense.description = description
    if amount is not None:
        db_expense.amount = amount
    if expense_date is not None:
        db_expense.expense_date = expense_date
    if currency is not None:
        db_expense.currency = currency

    session.flush()
    record_audit_log(
        session=session,
        actor_user_id=current_user_id,
        account_id=account_id,
        action="expense.updated",
        entity_type="expense",
        entity_id=expense_id,
        before=before,
        after=expense_snapshot(db_expense),
    )
    return db_expense


def delete_expense_by_id(session: Session, expense_id: UUID, current_user_id: UUID) -> None:
    db_expense = session.get(Expense, expense_id)
    if db_expense is None:
        raise ExpenseDoesNotExistError(expense_id=expense_id)

    access = require_account_writer(session=session, account_id=db_expense.account_id, user_id=current_user_id)
    current_user_is_owner = access.membership.role == MembershipRole.OWNER
    if all([not db_expense.created_by_user_id == current_user_id, not current_user_is_owner]):
        raise ExpenseDeleteForbiddenError(
            user_id=current_user_id, expense_id=expense_id, account_id=db_expense.account_id
        )

    before = expense_snapshot(db_expense)

    session.delete(db_expense)
    session.flush()
    record_audit_log(
        session=session,
        actor_user_id=current_user_id,
        account_id=before["account_id"],
        action="expense.deleted",
        entity_type="expense",
        entity_id=expense_id,
        before=before,
    )
    return None


def get_filtered_expenses(session: Session, params: ExpenseFilterParams, current_user_id: UUID):
    # 1. Reuse existing account logic
    db_account = get_account_by_id(session=session, account_id=params.account_id, current_user_id=current_user_id)

    ensure_account_mutable(
        account_id=params.account_id, account_status=db_account.status, operation=Operation.EXPENSE_READ
    )

    # 3. Base Query
    query = select(Expense).options(selectinload(Expense.category)).where(Expense.account_id == params.account_id)

    # 4. Filter by Status if provided in params
    if params.status:
        query = query.where(Expense.status.in_(params.status))

    # 5. Robust Search Logic (FTS)
    search_query = getattr(params, "search_query", None)
    if search_query and isinstance(search_query, str):
        search_input = search_query.strip()
        if search_input:
            search_str = f"{search_input}:*"
            query = query.where(
                func.to_tsvector("english", Expense.description).op("@@")(func.to_tsquery("english", search_str))
            )

    # 6. Apply Filters
    if params.start_date:
        query = query.where(Expense.expense_date >= params.start_date)
    if params.end_date:
        query = query.where(Expense.expense_date <= params.end_date)
    if params.category_id is not None:
        category = session.get(Category, params.category_id)
        if not category or category.account_id != params.account_id:
            raise CategoryNotFoundError(category_id=params.category_id)
        query = query.where(Expense.category_id == params.category_id)
    if params.min_amount is not None:
        query = query.where(Expense.amount >= params.min_amount)
    if params.max_amount is not None:
        query = query.where(Expense.amount <= params.max_amount)

    # 6. Aggregation (Get Total Count before Pagination)
    subq = query.subquery()
    total_count = session.execute(select(func.count()).select_from(subq)).scalar() or 0
    all_matching = session.execute(query.order_by(Expense.expense_date.desc())).scalars().all()

    # 7. Final Results (Paginated)
    final_query = query.order_by(Expense.expense_date.desc()).offset(params.offset).limit(params.limit)
    results = session.execute(final_query).scalars().all()

    return results, total_count, all_matching


def process_recurring_templates(session: Session, account_id: UUID | None = None) -> None:
    """Processes all active templates that are due as of today."""
    from datetime import date

    from ..db.models.expense import Expense, ExpenseStatus
    from ..db.models.recurring_template import RecurringTemplate
    from ..domain.expenses.recurring_logic import calculate_next_date

    today = date.today()

    # 1. Fetch active templates where next_occurrence_date is today or in the past.
    stmt = select(RecurringTemplate).where(
        RecurringTemplate.is_active.is_(True), RecurringTemplate.next_occurrence_date <= today
    )
    if account_id is not None:
        stmt = stmt.where(RecurringTemplate.account_id == account_id)
    templates = session.scalars(stmt).all()

    for tmpl in templates:
        while tmpl.next_occurrence_date <= today:
            calculated_user_share = ResponsibilityService().calculate_user_share(
                session=session,
                user_id=tmpl.created_by_user_id,
                account_id=tmpl.account_id,
                total_amount=tmpl.amount,
                personal_responsibility_factor=tmpl.personal_responsibility_factor,
            )

            # 2. Create the PENDING expense (The "Forecast")
            new_expense = Expense(
                account_id=tmpl.account_id,
                created_by_user_id=tmpl.created_by_user_id,
                category_id=tmpl.category_id,
                description=f"{tmpl.name}",  # Keeping it clean
                amount=tmpl.amount,
                currency=tmpl.currency,
                expense_date=tmpl.next_occurrence_date,
                status=ExpenseStatus.PENDING,
                global_event_id=tmpl.global_event_id,
                personal_responsibility_factor=tmpl.personal_responsibility_factor,
                calculated_user_share=calculated_user_share,
            )
            session.add(new_expense)

            # 3. Update the template for the next cycle
            tmpl.next_occurrence_date = calculate_next_date(
                anchor_date=tmpl.anchor_date, current_date=tmpl.next_occurrence_date, frequency=tmpl.frequency
            )

    session.flush()


def confirm_pending_expense(session: Session, expense_id: UUID, current_user_id: UUID) -> Expense:
    db_expense = session.get(Expense, expense_id)
    if not db_expense:
        raise ExpenseDoesNotExistError(expense_id=expense_id)

    require_account_writer(session=session, account_id=db_expense.account_id, user_id=current_user_id)

    if db_expense.status == ExpenseStatus.PENDING:
        before = expense_snapshot(db_expense)
        db_expense.status = ExpenseStatus.COMPLETED
        session.flush()
        record_audit_log(
            session=session,
            actor_user_id=current_user_id,
            account_id=db_expense.account_id,
            action="expense.approved",
            entity_type="expense",
            entity_id=expense_id,
            before=before,
            after=expense_snapshot(db_expense),
        )
        return db_expense

    session.flush()
    return db_expense


def get_recurring_templates_by_account(
    session: Session, account_id: UUID, current_user_id: UUID
) -> Sequence[RecurringTemplate]:
    db_account = session.get(Account, account_id)
    if not db_account:
        raise AccountDoesNotExistError(account_id=account_id)

    require_account_member(session=session, account_id=account_id, user_id=current_user_id)

    query = select(RecurringTemplate).where(RecurringTemplate.account_id == account_id)
    return session.scalars(query).all()
