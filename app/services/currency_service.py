import datetime
import os
from datetime import timedelta
from pathlib import Path
from typing import Any, Sequence

import httpx
from dotenv import load_dotenv
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..db.models.currency import CurrencyRate
from ..db.models.expense import Expense
from ..domain.currencies.currency import Currency

# Load dotenv
load_dotenv(Path(__file__).resolve().parent.parent / "../.env")


class CurrencyService:
    API_KEY = os.getenv("EXCHANGE_RATE_API_KEY")
    # Base URL remains static
    BASE_URL = f"https://v6.exchangerate-api.com/v6/{API_KEY}/latest"

    DEFAULT_CURRENCIES: list[str] = (os.getenv("DEFAULT_CURRENCIES") or "USD,EUR,GBP").split(",")
    STALE_THRESHOLD: float = float(os.getenv("STALE_THRESHOLD") or 6)

    async def fetch_latest_rates(self, base_currency: Currency) -> dict[str, float]:
        """Fetch rates from API using a specific base currency."""
        url = f"{self.BASE_URL}/{base_currency.value}"

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url)
                response.raise_for_status()
                data = response.json()
                return data.get("conversion_rates", {})
            except Exception:
                return {}

    @staticmethod
    def get_rate(db: Session, code: Currency) -> dict[str, Any] | None:
        rate_entry = db.query(CurrencyRate).filter(CurrencyRate.code == code.value).first()

        if not rate_entry:
            return None

        return {"rate": rate_entry.rate, "last_updated": rate_entry.updated_at.isoformat()}

    @classmethod
    def is_cache_stale(cls, last_updated: datetime.datetime) -> bool:
        return datetime.datetime.now(datetime.timezone.utc) > last_updated + timedelta(hours=cls.STALE_THRESHOLD)

    async def sync_rates(self, db: Session, base_currency: Currency = Currency.EUR):
        rates = await self.fetch_latest_rates(base_currency=base_currency)
        if not rates:
            return

        # Use a single timestamp for all entries in this batch
        now = datetime.datetime.now(datetime.timezone.utc)

        for code, rate in rates.items():
            db_rate = db.query(CurrencyRate).filter(CurrencyRate.code == code).first()
            if db_rate:
                db_rate.rate = rate
                db_rate.updated_at = now
            else:
                new_rate = CurrencyRate(code=code, rate=rate, updated_at=now)
                db.add(new_rate)

        # COMMIT ONCE after the loop for performance
        try:
            db.commit()
        except Exception as e:
            db.rollback()
            print(f"Database Error during sync: {e}")

    async def refresh_cache_if_stale(self, db: Session):
        latest_update = db.query(func.max(CurrencyRate.updated_at)).scalar()

        # Ensure we compare apples to apples with timezones
        if latest_update and latest_update.tzinfo is None:
            latest_update = latest_update.replace(tzinfo=datetime.timezone.utc)

        if not latest_update or self.is_cache_stale(last_updated=latest_update):
            await self.sync_rates(db=db, base_currency=Currency.EUR)

    async def get_normalized_total(self, db: Session, expenses: Sequence[Expense], target_currency: Currency) -> float:
        """
        Computes total sum. Uses DB if rates exist, regardless of staleness,
        to keep response times fast.
        """
        db_rates = db.query(CurrencyRate).all()

        if db_rates:
            all_rates = {(r.code.value if hasattr(r.code, "value") else r.code): float(r.rate) for r in db_rates}

            # Since our DB is synced with EUR base, we use EUR as the anchor
            # formula: (Amount / Source_Rate_in_EUR) * Target_Rate_in_EUR
            target_rate = all_rates.get(target_currency.value, 1.0)
            total = 0.0

            for exp in expenses:
                curr_val = exp.currency.value if hasattr(exp.currency, "value") else exp.currency
                if curr_val == target_currency.value:
                    total += float(exp.amount)
                else:
                    exp_rate = all_rates.get(curr_val)
                    if exp_rate:
                        total += (float(exp.amount) / exp_rate) * target_rate
                    else:
                        print(f"Warning: Missing rate for {curr_val}")
                        total += float(exp.amount)
            return round(total, 2)

        # Fallback only if DB is completely empty
        rates = await self.fetch_latest_rates(base_currency=target_currency)
        if not rates:
            return round(sum(float(e.amount) for e in expenses), 2)

        total = sum(float(exp.amount) / rates.get(exp.currency.value, 1.0) for exp in expenses)
        return round(total, 2)
