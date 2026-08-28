"""Authentication and token helpers."""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import secrets
import time
from uuid import UUID

PASSWORD_HASH_ITERATIONS = 210_000
TOKEN_TYPE = "bearer"


class AuthTokenError(ValueError):
    """Raised when an access token cannot be trusted."""


def _b64encode(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")


def _b64decode(encoded: str) -> bytes:
    padding = "=" * (-len(encoded) % 4)
    return base64.urlsafe_b64decode((encoded + padding).encode("ascii"))


def _auth_secret() -> bytes:
    secret = os.getenv("AUTH_SECRET_KEY")
    if secret:
        return secret.encode("utf-8")

    is_dev = os.getenv("DEV", "False").lower() == "true"
    is_test = os.getenv("TESTING", "False").lower() == "true"
    if is_dev or is_test:
        return b"dev-only-insecure-auth-secret"

    raise RuntimeError("AUTH_SECRET_KEY must be configured outside DEV/TESTING.")


def hash_password(password: str) -> str:
    """Hash a password with PBKDF2-SHA256."""
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, PASSWORD_HASH_ITERATIONS)
    return f"pbkdf2_sha256${PASSWORD_HASH_ITERATIONS}${_b64encode(salt)}${_b64encode(digest)}"


def verify_password(password: str, password_hash: str | None) -> bool:
    """Verify a raw password against a stored password hash."""
    if not password_hash:
        return False

    try:
        scheme, iterations, salt, expected = password_hash.split("$", 3)
    except ValueError:
        return False

    if scheme != "pbkdf2_sha256":
        return False

    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), _b64decode(salt), int(iterations))
    return hmac.compare_digest(_b64encode(digest), expected)


def create_access_token(user_id: UUID, expires_in_seconds: int | None = None) -> str:
    """Create a signed bearer token for a user id."""
    ttl = expires_in_seconds or int(os.getenv("ACCESS_TOKEN_EXPIRE_SECONDS", "86400"))
    payload = {"sub": str(user_id), "exp": int(time.time()) + ttl}
    payload_part = _b64encode(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
    signature = hmac.new(_auth_secret(), payload_part.encode("ascii"), hashlib.sha256).digest()
    return f"{payload_part}.{_b64encode(signature)}"


def verify_access_token(token: str) -> UUID:
    """Verify a signed bearer token and return its user id."""
    try:
        payload_part, signature_part = token.split(".", 1)
    except ValueError as exc:
        raise AuthTokenError("Invalid token format.") from exc

    expected_signature = hmac.new(_auth_secret(), payload_part.encode("ascii"), hashlib.sha256).digest()
    if not hmac.compare_digest(_b64encode(expected_signature), signature_part):
        raise AuthTokenError("Invalid token signature.")

    try:
        payload = json.loads(_b64decode(payload_part))
        expires_at = int(payload["exp"])
        user_id = UUID(payload["sub"])
    except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        raise AuthTokenError("Invalid token payload.") from exc

    if expires_at < int(time.time()):
        raise AuthTokenError("Token has expired.")

    return user_id
