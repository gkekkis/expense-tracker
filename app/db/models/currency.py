import datetime

from sqlalchemy import Column, DateTime, Enum, Float, func
from sqlalchemy.orm import Mapped, mapped_column

from ...domain.currencies.currency import Currency
from ..declarative_base import Base


class CurrencyRate(Base):
    __tablename__ = "currency_rates"
    code = Column(Enum(Currency, name="currency"), primary_key=True)
    rate = Column(Float, nullable=False)

    # Audit Timestamps
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, onupdate=func.now(), server_default=func.now()
    )
