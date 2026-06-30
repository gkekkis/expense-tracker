"""Blueprint module of the Account domain class."""

from __future__ import annotations

from datetime import date
from enum import Enum
from uuid import UUID, uuid4


class AccountStatus(Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"


class Account:
    """Account domain class."""

    def __init__(
        self,
        name: str,
        created_at: date,
        updated_at: date,
        status: AccountStatus = AccountStatus.ACTIVE,
        account_id: UUID | None = None,
        default_category_id: UUID | None = None,
    ) -> None:
        if not name or not str(name).strip():
            raise ValueError("Account name must not be empty or blank.")

        self.id: UUID = account_id or uuid4()
        self.default_category_id = default_category_id
        self.name: str = str(name).strip()
        self.created_at = created_at
        self.updated_at = updated_at
        self.status: AccountStatus = status

    def __repr__(self) -> str:
        return f"<id: {self.id}, name: {self.name}, status: {self.status}>"
