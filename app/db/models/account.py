"""Module containing DB Account model."""

from __future__ import annotations

import datetime
from uuid import uuid4

from sqlalchemy import Column, DateTime, Enum, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ...domain.accounts.account import AccountStatus
from ..declarative_base import Base


class Account(Base):
    __tablename__ = "accounts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, nullable=False, unique=True)
    name = Column(String, nullable=False)
    status = Column(Enum(AccountStatus), nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, onupdate=func.now(), server_default=func.now()
    )

    expenses = relationship("Expense", back_populates="account")
    memberships = relationship("Membership", back_populates="account")
    users = relationship("User", secondary="memberships", back_populates="accounts", viewonly=True)
