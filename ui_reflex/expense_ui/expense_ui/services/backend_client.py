from typing import Any, Literal

import httpx

from ..config import FASTAPI_BASE_URL


class ApiError(Exception):
    """UI-facing API error."""

    def __init__(self, message: str, status_code: int, error_code: str | None = None, payload: Any | None = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.payload = payload


def request(
    method: Literal["GET", "POST", "PATCH", "DELETE"],
    path: str,
    user_id: str,
    json: dict | None = None,
    params: dict | None = None,
) -> dict | list:
    """
    Generic HTTP client for calling the FastAPI backend.

    Returns parsed JSON (dict or list) on success.
    Raises ApiError on any non-2xx response.
    """
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

    # Try to parse JSON if possible
    payload: Any | None = None
    try:
        payload = response.json()
    except Exception:
        payload = None

    # Success path
    if response.is_success:
        return payload  # dict or list

    # Error path: normalize all errors into ApiError
    message = f"Request failed ({response.status_code})"
    error_code = None

    if isinstance(payload, dict):
        # Your custom backend error format
        if "detail" in payload:
            message = payload["detail"]
        if "error_code" in payload:
            error_code = payload["error_code"]

    elif isinstance(payload, list):
        # FastAPI 422 validation errors
        message = " | ".join(f"{'.'.join(map(str, item.get('loc', [])))}: {item.get('msg', '')}" for item in payload)

    raise ApiError(message=message, status_code=response.status_code, error_code=error_code, payload=payload)
