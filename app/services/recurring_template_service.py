"""Recurring template service (CRUD).

Permission model (A):
- VIEWER: read-only
- MEMBER: can create templates; can update/delete only templates they created
- OWNER: can update/delete any template

This mirrors your expense rules (OWNER or creator can update/delete).
"""

from __future__ import annotations

from datetime import date
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db.models.account import Account
from ..db.models.membership import Membership
from ..db.models.recurring_template import RecurringTemplate
from ..domain.expenses.recurring_logic import calculate_next_date
from ..domain.memberships.membership import MembershipRole
from ..errors.errors import (
    AccountDoesNotExistError,
    RecurringTemplateCreateForbiddenError,
    RecurringTemplateDoesNotExistError,
    RecurringTemplateUpdateForbiddenError,
)
from ..schemas.recurring_template import RecurringTemplateCreate, RecurringTemplateUpdate
from .authorization_service import require_account_member


def _get_membership(session: Session, account_id: UUID, user_id: UUID) -> Membership:
    return require_account_member(session=session, account_id=account_id, user_id=user_id).membership


def _ensure_can_mutate(membership: Membership, tmpl: RecurringTemplate, user_id: UUID) -> None:
    if membership.role == MembershipRole.OWNER:
        return

    if membership.role == MembershipRole.MEMBER and tmpl.created_by_user_id == user_id:
        return

    raise RecurringTemplateUpdateForbiddenError(
        user_id=user_id, recurring_template_id=tmpl.id, account_id=tmpl.account_id
    )


def list_by_account(session: Session, account_id: UUID, current_user_id: UUID) -> list[RecurringTemplate]:
    if session.get(Account, account_id) is None:
        raise AccountDoesNotExistError(account_id=account_id)

    _get_membership(session=session, account_id=account_id, user_id=current_user_id)

    query = (
        select(RecurringTemplate)
        .where(RecurringTemplate.account_id == account_id)
        .order_by(RecurringTemplate.next_occurrence_date.asc(), RecurringTemplate.name.asc())
    )
    return list(session.scalars(query).all())


def create(session: Session, current_user_id: UUID, payload: RecurringTemplateCreate) -> RecurringTemplate:
    if session.get(Account, payload.account_id) is None:
        raise AccountDoesNotExistError(account_id=payload.account_id)

    membership = _get_membership(session=session, account_id=payload.account_id, user_id=current_user_id)

    # MEMBER and OWNER can create; VIEWER cannot.
    if membership.role not in (MembershipRole.MEMBER, MembershipRole.OWNER):
        raise RecurringTemplateCreateForbiddenError(user_id=current_user_id, account_id=payload.account_id)

    tmpl = RecurringTemplate(**payload.model_dump())
    tmpl.created_by_user_id = current_user_id

    # Initialize next occurrence date.
    # If anchor is in the future: next occurrence is anchor.
    # Otherwise: move forward from today using the recurring logic.
    today = date.today()
    if payload.anchor_date >= today:
        tmpl.next_occurrence_date = payload.anchor_date
    else:
        tmpl.next_occurrence_date = calculate_next_date(
            anchor_date=payload.anchor_date, current_date=today, frequency=payload.frequency
        )

    session.add(tmpl)
    session.flush()
    return tmpl


def update(
    session: Session, current_user_id: UUID, template_id: UUID, payload: RecurringTemplateUpdate
) -> RecurringTemplate:
    tmpl = session.get(RecurringTemplate, template_id)
    if not tmpl:
        raise RecurringTemplateDoesNotExistError(recurring_template_id=template_id)

    membership = _get_membership(session=session, account_id=tmpl.account_id, user_id=current_user_id)
    _ensure_can_mutate(membership=membership, tmpl=tmpl, user_id=current_user_id)

    update_dict = payload.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(tmpl, key, value)

    # If scheduling parameters changed, recompute next_occurrence_date forward from today.
    if "anchor_date" in update_dict or "frequency" in update_dict:
        today = date.today()
        tmpl.next_occurrence_date = (
            tmpl.anchor_date
            if tmpl.anchor_date >= today
            else calculate_next_date(tmpl.anchor_date, today, tmpl.frequency)
        )

    session.flush()
    return tmpl


def delete(session: Session, current_user_id: UUID, template_id: UUID) -> None:
    tmpl = session.get(RecurringTemplate, template_id)
    if not tmpl:
        raise RecurringTemplateDoesNotExistError(recurring_template_id=template_id)

    membership = _get_membership(session=session, account_id=tmpl.account_id, user_id=current_user_id)
    _ensure_can_mutate(membership=membership, tmpl=tmpl, user_id=current_user_id)

    session.delete(tmpl)
    session.flush()
