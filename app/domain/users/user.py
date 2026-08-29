"""Blueprint module of the User domain class."""

from __future__ import annotations

from enum import Enum
from typing import Optional
from uuid import UUID, uuid4


class UserStatus(Enum):
    ACTIVE = "ACTIVE"
    LOCKED = "LOCKED"
    DISABLED = "DISABLED"


class User:
    """User domain class."""

    def __init__(
        self, name: str, status: UserStatus, email: Optional[str] = None, user_id: Optional[UUID] = None
    ) -> None:
        # Let caller optionally pass an existing UUID (e.g. loaded from DB),
        # otherwise generate a new one for domain usage.
        self.id: UUID = user_id or uuid4()
        self.name: str = name
        self.status: UserStatus = status
        self.email: Optional[str] = email

    def __repr__(self) -> str:
        details = f"<id: {self.id}, name: {self.name}, status: {self.status}, email: {self.email}>"
        return details
