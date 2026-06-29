from __future__ import annotations

import os
from typing import Any, Dict, Optional

import httpx

API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8001").rstrip("/")


class ApiError(Exception):
    def __init__(self, status_code: int, detail: str | None = None, payload: Any | None = None):
        self.status_code = status_code
        self.detail = detail or "Request failed"
        self.payload = payload
        super().__init__(f"HTTP {status_code}: {self.detail}")


def _headers(user_id: str | None) -> Dict[str, str]:
    h: Dict[str, str] = {"Accept": "application/json"}
    if user_id:
        h["X-User-Id"] = user_id
    return h


async def request(
    method: str,
    path: str,
    *,
    user_id: str | None = None,
    params: Optional[Dict[str, Any]] = None,
    json: Any | None = None,
    timeout: float = 20.0,
) -> Any:
    url = f"{API_BASE_URL}{path}"
    async with httpx.AsyncClient(timeout=timeout) as client:
        resp = await client.request(method, url, headers=_headers(user_id), params=params, json=json)

    if resp.status_code >= 400:
        detail = None
        payload = None
        try:
            payload = resp.json()
            # FastAPI commonly uses {"detail": ...}
            if isinstance(payload, dict) and "detail" in payload:
                detail = str(payload["detail"])
        except Exception:
            payload = resp.text
        raise ApiError(resp.status_code, detail=detail, payload=payload)

    if resp.status_code == 204:
        return None

    # Some endpoints might return empty body
    if not resp.content:
        return None

    return resp.json()
