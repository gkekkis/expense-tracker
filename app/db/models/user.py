"""Module containing DB User model."""

from __future__ import annotations

import datetime
from uuid import uuid4

from sqlalchemy import Column, DateTime, Enum, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ...domain.users.user import UserStatus
from ..declarative_base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,  # SQLAlchemy will call uuid4() when inserting
        unique=True,
        nullable=False,
    )
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=True)
    password_hash = Column(String, nullable=True)
    status = Column(Enum(UserStatus), nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    memberships = relationship("Membership", back_populates="user")
    accounts = relationship("Account", secondary="memberships", back_populates="users", viewonly=True)
