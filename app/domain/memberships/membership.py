"""Blueprint module of the Membership domain types."""

from __future__ import annotations

from enum import Enum


class MembershipRole(Enum):
    OWNER = "OWNER"
    MEMBER = "MEMBER"
    VIEWER = "VIEWER"
