"""Module containing DB RecurringTemplate model with for recurring (e.g, subscriptions) expenses."""

from __future__ import annotations

from uuid import uuid4

from sqlalchemy import Boolean, Column, Date, Enum, ForeignKey, Numeric, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID

from ...domain.currencies.currency import Currency
from ...domain.frequency_type import FrequencyType
from ..declarative_base import Base


class RecurringTemplate(Base):
    __tablename__ = "recurring_templates"
    __table_args__ = (
        UniqueConstraint("account_id", "name", name="uq_recurring_name_per_account"),
        UniqueConstraint("account_id", "icon", name="uq_exp_icon_per_account"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, nullable=False, unique=True)
    account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id"), nullable=False)
    # Used for permissioning: MEMBERS can manage templates they created; OWNER can manage all.
    created_by_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id"), nullable=False)
    description = Column(String, nullable=False)
    name = Column(String, nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(Enum(Currency, name="currency"), nullable=False, default=Currency.EUR)

    global_event_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    personal_responsibility_factor = Column(Numeric(3, 2), nullable=True)

    frequency = Column(Enum(FrequencyType, name="frequency"), nullable=False, default=FrequencyType.MONTHLY)
    anchor_date = Column(Date, nullable=False)
    next_occurrence_date = Column(Date, nullable=False)
    is_active = Column(Boolean)
    icon = Column(String, nullable=False)
