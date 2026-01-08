"""
DEV-ONLY: Reset the database schema by dropping and recreating all tables.

⚠️ DANGER:
- This will DELETE ALL DATA in the configured database.
- Do NOT run in production.
- Do NOT import this module from the FastAPI app.
"""

from __future__ import annotations

import os
import sys

from sqlalchemy import text

from app.db.base import Base

# Import your engine + Base
from app.db.engine import engine
from app.db.models.account import Account  # noqa: F401
from app.db.models.expense import Expense  # noqa: F401
from app.db.models.membership import Membership  # noqa: F401

# IMPORTANT:
# Ensure all models are imported so they are registered in Base.metadata.
# If you have a central models import file, import it here.
# Otherwise, import each model module explicitly.
from app.db.models.user import User  # noqa: F401


def reset_db(*, require_confirm: bool = True) -> None:
    """
    Drops all tables and recreates them.

    require_confirm:
        If True, requires the user to type 'RESET' in the console.
    """
    if require_confirm:
        print("⚠️  DEV-ONLY DB RESET")
        print("This will DROP ALL TABLES and DELETE ALL DATA in the target database.")
        confirm = input("Type RESET to continue: ").strip()
        if confirm != "RESET":
            print("Aborted.")
            return

    # Optional safety: you can require an environment flag
    # e.g. export ALLOW_DB_RESET=1
    if os.getenv("ALLOW_DB_RESET") != "1":
        print("Refusing to run because ALLOW_DB_RESET is not set to '1'.")
        print("Set it temporarily and rerun:")
        print("  Windows PowerShell:  $env:ALLOW_DB_RESET='1'")
        print("  macOS/Linux:         export ALLOW_DB_RESET=1")
        return

    print("Connecting and dropping all tables...")
    # If you have FK dependencies, dropping in the right order can be tricky.
    # drop_all handles it generally, but for Postgres we can also drop schema objects more aggressively if needed.
    Base.metadata.drop_all(bind=engine)

    print("Creating all tables...")
    Base.metadata.create_all(bind=engine)

    # Optional sanity check: lightweight query
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
        conn.commit()

    print("✅ Database reset complete.")


if __name__ == "__main__":
    try:
        reset_db(require_confirm=True)
    except KeyboardInterrupt:
        print("\nAborted.")
        sys.exit(1)
