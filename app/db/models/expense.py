"""Module containing DB Expense model with advanced indexing."""

from __future__ import annotations

import datetime
from uuid import uuid4

from sqlalchemy import Column, Date, DateTime, Enum, ForeignKey, Index, Numeric, String, event, func, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ...domain.currencies.currency import Currency
from ...domain.expenses.expense import ExpenseCategory
from ..declarative_base import Base


class Expense(Base):
    __tablename__ = "expenses"

    # Core Fields
    id = Column(UUID(as_uuid=True), default=uuid4, primary_key=True)

    account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id"), nullable=False)
    created_by_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    description = Column(String, nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)

    category = Column(Enum(ExpenseCategory, name="expensecategory"), nullable=False)
    expense_date = Column(Date, nullable=False)
    currency = Column(Enum(Currency, name="currency"), nullable=False, default=Currency.EUR)

    # Audit Timestamps
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, onupdate=func.now(), server_default=func.now()
    )

    # Relationships
    account = relationship("Account", back_populates="expenses")
    created_by_user = relationship("User")

    __table_args__ = (
        # 1. Dashboard Index: Filters by account and sorts by date (newest first)
        Index("ix_expenses_account_date", "account_id", expense_date.desc()),
        # 2. Reporting Index: Filters by category within an account
        Index("ix_expenses_account_category", "account_id", "category"),
        # 3. GIN Full-Text Search Index:
        # Converts 'description' to a searchable vector.
        # Using 'english' config ignores common words like 'the' or 'a'.
        Index("ix_expenses_description_fts", text("to_tsvector('english', description)"), postgresql_using="gin"),
    )


# Place this immediately after the class
@event.listens_for(Expense.__table__, "before_create")
def remove_search_index(target, connection, **kw):
    """
    Forcefully drops the GIN index from the DDL instructions
    if the database engine is SQLite.
    """
    if connection.engine.dialect.name == "sqlite":
        target.indexes = {idx for idx in target.indexes if idx.name != "ix_expenses_description_fts"}
