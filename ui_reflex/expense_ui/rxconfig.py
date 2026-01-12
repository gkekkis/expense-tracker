import os

import reflex as rx
from dotenv import load_dotenv

dotenv_loaded = load_dotenv("../../.env")


if not os.getenv("DEV"):
    database_url = os.getenv("DATABASE_URL", "sqlite:///reflex.db")
else:
    database_url = os.getenv("TEST_DATABASE_URL", "sqlite:///reflex.db")


config = rx.Config(
    app_name="expense_ui",
    frontend_port=3000,
    backend_port=8001,
    api_url="http://localhost:8001",
    db_url=database_url,
    plugins=[rx.plugins.SitemapPlugin()],
    initial_color_mode="system",
)
