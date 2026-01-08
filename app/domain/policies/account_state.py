"""Module including helper functions that support policy checks."""

from __future__ import annotations

import logging
from uuid import UUID

logger = logging.getLogger(__name__)

from ...errors.errors import AccountInactiveError
from ..accounts.account import AccountStatus
from ..operations import Operation


def ensure_account_mutable(account_id: UUID, account_status: AccountStatus, operation: Operation) -> None:
    if account_status != AccountStatus.ACTIVE:
        raise AccountInactiveError(account_id=account_id, operation=operation)


def ensure_inactive_account_reactivation_only(
    *, account_id: UUID, account_status: AccountStatus, operation: Operation, other_fields_provided: bool
) -> None:
    if account_status == AccountStatus.INACTIVE and other_fields_provided:
        raise AccountInactiveError(account_id=account_id, operation=operation)
