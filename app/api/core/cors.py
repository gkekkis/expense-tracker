"""CORS configuration helpers."""

from __future__ import annotations

import os


def get_cors_allow_origins() -> list[str]:
    """Return configured browser origins allowed to call the API."""
    raw_origins = os.getenv("CORS_ALLOW_ORIGINS", "")
    return [origin.strip().rstrip("/") for origin in raw_origins.split(",") if origin.strip()]
