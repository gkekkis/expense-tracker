"""Module containing DB Category model for expense categories."""

from __future__ import annotations

from uuid import uuid4

from sqlalchemy import Column, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID

from ..declarative_base import Base


class Category(Base):
    __tablename__ = "categories"
    __table_args__ = (
        UniqueConstraint("account_id", "name", name="uq_exp_category_per_account"),
        UniqueConstraint("account_id", "emoji", name="uq_exp_emoji_per_account"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, nullable=False, unique=True)
    account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id"), nullable=False)
    name = Column(String, nullable=False)
    emoji = Column(String, nullable=False)
