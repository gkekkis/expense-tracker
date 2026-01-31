import os
from logging.config import fileConfig
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import engine_from_config, pool

from alembic import context
from app.db import models  # noqa: F401
from app.db.base import Base

# 1. Setup path and load .env
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


# 2. Dynamic URL Selection Logic
def get_url():
    is_dev = os.getenv("DEV", "False").lower() == "true"
    is_test = os.getenv("TESTING", "False").lower() == "true"

    assert is_dev != is_test, f"DEV and TESTING flags must not be equal.\nDEV: `{is_dev}`\tTESTING: `{is_test}`"

    if is_dev:
        # Priority for the test database during development
        url = os.getenv("TEST_DATABASE_URL")
    elif is_test:
        url = os.getenv("PYTEST_DATABASE_URL")
    else:
        # Use the standard URL for production/other environments
        url = os.getenv("DATABASE_URL")

    return url


# 3. Configure Alembic to use the selected URL
database_url = get_url()
config = context.config

if database_url:
    config.set_main_option("sqlalchemy.url", database_url)
else:
    raise ValueError("No database URL found in environment variables!")

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """
    Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url, target_metadata=target_metadata, literal_binds=True, dialect_opts={"paramstyle": "named"}
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}), prefix="sqlalchemy.", poolclass=pool.NullPool
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
