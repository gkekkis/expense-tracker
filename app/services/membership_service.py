"""Module containign User session functionalities."""

from __future__ import annotations

from decimal import Decimal
from typing import Sequence
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session  # noqa: TCH002

from ..db.models.account import Account
from ..db.models.membership import Membership
from ..domain.memberships.membership import MembershipRole
from ..domain.operations import Operation
from ..domain.policies.account_state import ensure_account_mutable
from ..errors.errors import (
    AccountDoesNotExistError,
    MembershipAlreadyExistError,
    MembershipCreateForbiddenError,
    MembershipDeleteForbiddenError,
    MembershipDoesNotExistError,
    MembershipFirstOwnerRequiredError,
    MembershipLastOwnerDeleteForbiddenError,
    MembershipLastOwnerDemoteForbiddenError,
    MembershipUpdateForbiddenError,
    MembershipUpdateNoFieldsProvidedError,
)
from ..schemas.membership import MembershipCreate  # noqa: TCH001
from .audit_log_service import membership_snapshot, record_audit_log
from .authorization_service import get_account_ids_for_user, require_account_member


def create_membership(session: Session, membership: MembershipCreate, current_user_id: UUID) -> Membership:
    db_membership = Membership(
        user_id=membership.user_id,
        account_id=membership.account_id,
        role=membership.role,
        default_contribution_share=membership.default_contribution_share,
    )

    try:
        # Check if account exists
        account_exists = session.scalar(select(1).where(Account.id == membership.account_id)) is not None
        if not account_exists:
            raise AccountDoesNotExistError(account_id=membership.account_id)

        # Check if account is active
        account_status = session.scalar(select(Account.status).where(Account.id == membership.account_id))
        ensure_account_mutable(
            account_id=membership.account_id, account_status=account_status, operation=Operation.MEMBERSHIP_CREATE
        )

        # Check if account has 0 memberships and the role is not OWNER
        num_of_account_memberships = session.scalar(
            select(func.count(Membership.user_id)).where(Membership.account_id == membership.account_id)
        )

        if num_of_account_memberships == 0:
            if membership.user_id != current_user_id or membership.role != MembershipRole.OWNER:
                raise MembershipFirstOwnerRequiredError(account_id=membership.account_id)
        else:
            # Check if current user is OWNER
            is_owner = (
                session.scalar(
                    select(1).where(
                        Membership.user_id == current_user_id,
                        Membership.account_id == membership.account_id,
                        Membership.role == MembershipRole.OWNER,
                    )
                )
                is not None
            )
            if not is_owner:
                raise MembershipCreateForbiddenError(user_id=current_user_id, account_id=membership.account_id)

        session.add(db_membership)
        session.flush()
        record_audit_log(
            session=session,
            actor_user_id=current_user_id,
            account_id=db_membership.account_id,
            action="membership.created",
            entity_type="membership",
            entity_id=db_membership.id,
            after=membership_snapshot(db_membership),
        )
    except IntegrityError as e:
        session.rollback()
        raise MembershipAlreadyExistError(user_id=membership.user_id, account_id=membership.account_id) from e

    return db_membership


def get_all_memberships(session: Session, current_user_id: UUID) -> Sequence[Membership]:
    account_ids = get_account_ids_for_user(session=session, user_id=current_user_id)
    if not account_ids:
        return []
    return session.scalars(select(Membership).where(Membership.account_id.in_(account_ids))).all()


def get_membership_by_id(session: Session, membership_id: UUID, current_user_id: UUID) -> Membership:
    db_membership = session.get(Membership, membership_id)
    if db_membership is None:
        raise MembershipDoesNotExistError(membership_id=membership_id)
    require_account_member(session=session, account_id=db_membership.account_id, user_id=current_user_id)
    return db_membership


def update_membership_by_id(
    session: Session,
    membership_id: UUID,
    current_user_id: UUID,
    role: MembershipRole | None = None,
    default_contribution_share: Decimal | None = None,
) -> Membership:
    db_membership = session.get(Membership, membership_id)
    # Check if update has values
    if role is None and default_contribution_share is None:
        raise MembershipUpdateNoFieldsProvidedError(membership_id=membership_id)

    # Check if membership exists
    if db_membership is None:
        raise MembershipDoesNotExistError(membership_id=membership_id)

    # If exists use helper function to check if it is active. If not raise error
    account_id = db_membership.account_id
    account_status = session.scalar(select(Account.status).where(Account.id == db_membership.account_id))

    # Check if account exists
    if account_status is None:
        raise AccountDoesNotExistError(account_id=account_id)

    # Check if current user is OWNER
    statement = (
        select(1).where(
            Membership.user_id == current_user_id,
            Membership.account_id == db_membership.account_id,
            Membership.role == MembershipRole.OWNER,
        )
    ).limit(1)
    current_user_is_owner = session.scalar(statement) is not None

    if not current_user_is_owner:
        raise MembershipUpdateForbiddenError(
            user_id=current_user_id, membership_id=membership_id, account_id=account_id
        )

    # Add demotion guard to avoid PATCH an OWNER to MEMBER and end up with 0 owners
    before = membership_snapshot(db_membership)

    owners_count = session.scalar(
        select(func.count(Membership.user_id.distinct())).where(
            Membership.role == MembershipRole.OWNER, Membership.account_id == account_id
        )
    )
    if (
        role is not None
        and db_membership.role == MembershipRole.OWNER
        and role != MembershipRole.OWNER
        and owners_count == 1
    ):
        raise MembershipLastOwnerDemoteForbiddenError(
            user_id=current_user_id, membership_id=membership_id, account_id=account_id
        )

    # Ensure account is mutable
    ensure_account_mutable(account_id=account_id, account_status=account_status, operation=Operation.MEMBERSHIP_UPDATE)

    if role is not None:
        db_membership.role = role
    if default_contribution_share is not None:
        db_membership.default_contribution_share = default_contribution_share

    session.flush()
    record_audit_log(
        session=session,
        actor_user_id=current_user_id,
        account_id=account_id,
        action="membership.updated",
        entity_type="membership",
        entity_id=membership_id,
        before=before,
        after=membership_snapshot(db_membership),
    )

    return db_membership


def delete_membership_by_id(session: Session, membership_id: UUID, current_user_id: UUID) -> None:
    db_membership = session.get(Membership, membership_id)
    # Check if membership exists
    if db_membership is None:
        raise MembershipDoesNotExistError(membership_id=membership_id)

    # If exists use helper function to check if it is active. If not raise error
    account_id = db_membership.account_id
    account_status = session.scalar(select(Account.status).where(Account.id == db_membership.account_id))

    # Check if account exists
    if account_status is None:
        raise AccountDoesNotExistError(account_id=account_id)

    # Check if current user is OWNER
    statement = (
        select(1).where(
            Membership.user_id == current_user_id,
            Membership.account_id == db_membership.account_id,
            Membership.role == MembershipRole.OWNER,
        )
    ).limit(1)
    current_user_is_owner = session.scalar(statement) is not None

    if not current_user_is_owner:
        raise MembershipDeleteForbiddenError(
            user_id=current_user_id, membership_id=membership_id, account_id=account_id
        )

    # Ensure account is mutable
    ensure_account_mutable(account_id=account_id, account_status=account_status, operation=Operation.MEMBERSHIP_DELETE)

    # Add guard to not delete the last OWNER, because the account becomes unmanaged
    num_of_membership_owners = session.scalar(
        select(func.count(Membership.user_id.distinct())).where(
            Membership.role == MembershipRole.OWNER, Membership.account_id == account_id
        )
    )
    if db_membership.role == MembershipRole.OWNER and num_of_membership_owners == 1:
        raise MembershipLastOwnerDeleteForbiddenError(
            user_id=current_user_id, membership_id=membership_id, account_id=account_id
        )

    before = membership_snapshot(db_membership)

    # Delete membership
    session.delete(db_membership)

    session.flush()
    record_audit_log(
        session=session,
        actor_user_id=current_user_id,
        account_id=account_id,
        action="membership.deleted",
        entity_type="membership",
        entity_id=membership_id,
        before=before,
    )

    return None
