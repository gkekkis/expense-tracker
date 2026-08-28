"""Helpers for writing account-scoped audit logs."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from ..db.models.account import Account
from ..db.models.audit_log import AuditLog
from ..db.models.expense import Expense
from ..db.models.financial_profile import FinancialProfile
from ..db.models.membership import Membership


def _jsonable(value: Any) -> Any:
    if isinstance(value, UUID):
        return str(value)
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, datetime | date):
        return value.isoformat()
    return value


def _clean_snapshot(snapshot: dict[str, Any] | None) -> dict[str, Any] | None:
    if snapshot is None:
        return None
    return {key: _jsonable(value) for key, value in snapshot.items()}


def account_snapshot(account: Account) -> dict[str, Any]:
    return {
        "id": account.id,
        "name": account.name,
        "status": account.status,
        "default_category_id": account.default_category_id,
    }


def membership_snapshot(membership: Membership) -> dict[str, Any]:
    return {
        "id": membership.id,
        "user_id": membership.user_id,
        "account_id": membership.account_id,
        "role": membership.role,
        "default_contribution_share": membership.default_contribution_share,
    }


def expense_snapshot(expense: Expense) -> dict[str, Any]:
    return {
        "id": expense.id,
        "account_id": expense.account_id,
        "created_by_user_id": expense.created_by_user_id,
        "description": expense.description,
        "amount": expense.amount,
        "category_id": expense.category_id,
        "status": expense.status,
        "expense_date": expense.expense_date,
        "currency": expense.currency,
        "global_event_id": expense.global_event_id,
        "personal_responsibility_factor": expense.personal_responsibility_factor,
        "calculated_user_share": expense.calculated_user_share,
    }


def financial_profile_snapshot(profile: FinancialProfile) -> dict[str, Any]:
    return {
        "id": profile.id,
        "account_id": profile.account_id,
        "monthly_net_income": profile.monthly_net_income,
        "savings_percentage_goal": profile.savings_percentage_goal,
        "emergency_fund_target": profile.emergency_fund_target,
    }


def record_audit_log(
    session: Session,
    *,
    actor_user_id: UUID | None,
    account_id: UUID | None,
    action: str,
    entity_type: str,
    entity_id: UUID | None,
    before: dict[str, Any] | None = None,
    after: dict[str, Any] | None = None,
) -> AuditLog:
    audit_log = AuditLog(
        actor_user_id=actor_user_id,
        account_id=account_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        before=_clean_snapshot(before),
        after=_clean_snapshot(after),
    )
    session.add(audit_log)
    session.flush()
    return audit_log
