from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

import httpx

from ..config import FASTAPI_BASE_URL


@dataclass
class ApiError(Exception):
    message: str
    status_code: int
    error_code: str | None = None
    payload: Any | None = None


def request(
    method: Literal["GET", "POST", "PATCH", "DELETE"],
    path: str,
    user_id: str,
    json: dict | None = None,
    params: dict | None = None,
) -> dict | list:
    """Call FastAPI backend and return parsed JSON (dict|list). Raise ApiError otherwise."""
    url = FASTAPI_BASE_URL.rstrip("/") + "/" + path.lstrip("/")

    response = httpx.request(
        method=method,
        url=url,
        headers={"X-User-Id": user_id},
        json=json,
        params=params,
        follow_redirects=True,
        timeout=10,
    )

    payload: Any | None
    try:
        payload = response.json()
    except Exception:
        payload = None

    if response.is_success:
        return payload

    message = f"Request failed ({response.status_code})"
    error_code = None

    # Your custom error format: {"error_code": "...", "detail": "...", "path": "..."}
    if isinstance(payload, dict):
        if "detail" in payload:
            message = payload["detail"]
        if "error_code" in payload:
            error_code = payload["error_code"]

    # FastAPI 422 format
    if isinstance(payload, dict) and "detail" in payload and isinstance(payload["detail"], list):
        parts = []
        for item in payload["detail"]:
            loc = ".".join(str(x) for x in item.get("loc", []))
            msg = item.get("msg", "")
            parts.append(f"{loc}: {msg}")
        message = " | ".join(parts)

    raise ApiError(message=message, status_code=response.status_code, error_code=error_code, payload=payload)
