"""Module for initializing the db package with professional indexes."""

from .base import Base
from .engine import engine

# Import models to ensure they are registered with Base.metadata
from .models.account import Account  # noqa: F401
from .models.currency import CurrencyRate  # noqa: F401
from .models.expense import Expense  # noqa: F401
from .models.financial_profile import FinancialProfile  # noqa: F401
from .models.membership import Membership  # noqa: F401
from .models.user import User  # noqa: F401


def init_db():
    print(f"📡 Connecting to: {engine.url.database}")

    # Check if we have models registered
    if not Base.metadata.tables:
        print("❌ Error: No models found. Check your import paths.")
        return

    # DROP and CREATE is the only way to sync indexes without Alembic
    print("🗑️ Dropping existing tables to refresh schema...")
    Base.metadata.drop_all(engine)

    print("🏗️ Creating tables with Composite & GIN indexes...")
    Base.metadata.create_all(engine)

    print(f"✅ Success! Tables created: {', '.join(Base.metadata.tables.keys())}")


if __name__ == "__main__":
    init_db()
