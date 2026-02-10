"""Module for configuring the SQLAlchemy engine."""

from pathlib import Path

from dotenv import load_dotenv

dotenv_loaded = load_dotenv(Path(__file__).resolve().parent.parent / "../.env")

import os

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

# 2. Read DB settings from environment
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_host = os.getenv("DB_HOST")
db_port = os.getenv("DB_PORT")
db_name = os.getenv("DB_NAME")

# 3. Fail fast if any required variable is missing
missing_vars = [
    name
    for name, value in {
        "DB_USER": db_user,
        "DB_PASSWORD": db_password,
        "DB_HOST": db_host,
        "DB_PORT": db_port,
        "DB_NAME": db_name,
    }.items()
    if not value
]

if missing_vars:
    missing_str = ", ".join(missing_vars)
    raise RuntimeError(
        f"Missing required environment variables: {missing_str}. "
        "Make sure your .env file is in the project root and load_dotenv() is called."
    )

# 4. Build the database URL using the env values
is_dev = os.getenv("DEV", "False").lower() == "true"
is_test = os.getenv("TESTING", "False").lower() == "true"

assert not (
    is_dev and is_test
), f"DEV and TESTING flags must not be both `True`.\nDEV: `{is_dev}`\tTESTING: `{is_test}`"

if is_dev:
    DATABASE_URL = os.getenv("TEST_DATABASE_URL")
elif is_test:
    DATABASE_URL = os.getenv("PYTEST_DATABASE_URL")
else:
    DATABASE_URL = f"postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

# 5. Create the SQLAlchemy engine
engine: Engine = create_engine(DATABASE_URL)
