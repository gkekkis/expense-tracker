"""Module containing DB Membership model."""

from __future__ import annotations

import datetime
from uuid import uuid4

from sqlalchemy import Column, DateTime, Enum, ForeignKey, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ...domain.memberships.membership import MembershipRole
from ..declarative_base import Base


class Membership(Base):
    __tablename__ = "memberships"
    __table_args__ = (UniqueConstraint("user_id", "account_id", name="uq_membership_user_account"),)

    id = Column(UUID(as_uuid=True), default=uuid4, primary_key=True, nullable=False, unique=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id"), nullable=False)
    role = Column(Enum(MembershipRole), nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    user = relationship("User", back_populates="memberships")
    account = relationship("Account", back_populates="memberships")
