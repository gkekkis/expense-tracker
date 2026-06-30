from __future__ import annotations

from app.api.core.security import hash_password
from app.api.dependencies import get_current_user_id
from app.db.models.user import User
from app.domain.users.user import UserStatus


def test_login_returns_bearer_token_and_authenticates_me(client, db_session):
    user = User(
        name="Auth User",
        email="auth@example.com",
        password_hash=hash_password("correct-password"),
        status=UserStatus.ACTIVE,
    )
    db_session.add(user)
    db_session.flush()

    login_resp = client.post("/api/v1/auth/login", json={"email": "auth@example.com", "password": "correct-password"})

    assert login_resp.status_code == 200, login_resp.text
    body = login_resp.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]

    client.app.dependency_overrides.pop(get_current_user_id, None)
    me_resp = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {body['access_token']}"})

    assert me_resp.status_code == 200, me_resp.text
    assert me_resp.json()["id"] == str(user.id)


def test_login_rejects_wrong_password(client, db_session):
    user = User(
        name="Auth User",
        email="auth2@example.com",
        password_hash=hash_password("correct-password"),
        status=UserStatus.ACTIVE,
    )
    db_session.add(user)
    db_session.flush()

    resp = client.post("/api/v1/auth/login", json={"email": "auth2@example.com", "password": "wrong-password"})

    assert resp.status_code == 401


def test_protected_endpoint_requires_auth_without_override(client):
    client.app.dependency_overrides.pop(get_current_user_id, None)

    resp = client.get("/api/v1/users/me/accounts")

    assert resp.status_code == 401
    assert resp.json()["detail"] == "Bearer token missing."
