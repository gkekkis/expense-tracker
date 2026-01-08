"""Blueprint module of the Account domain class."""

from __future__ import annotations

from enum import Enum
from uuid import UUID, uuid4


class AccountStatus(Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"


class Account:
    """Account domain class."""

    def __init__(self, name: str, status: AccountStatus = AccountStatus.ACTIVE, account_id: UUID | None = None) -> None:
        if not name or not str(name).strip():
            raise ValueError("Account name must not be empty or blank.")

        self.id: UUID = account_id or uuid4()
        self.name: str = str(name).strip()
        self.status: AccountStatus = status

    def __repr__(self) -> str:
        return f"<id: {self.id}, name: {self.name}, status: {self.status}>"
