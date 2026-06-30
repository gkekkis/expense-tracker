from __future__ import annotations

from uuid import UUID

from conftest import seed_account, seed_category, seed_membership, seed_user
from sqlalchemy import select

from app.db.models.audit_log import AuditLog
from app.db.models.membership import MembershipRole
from app.domain.accounts.account import AccountStatus


def _logs_for_action(db_session, action: str) -> list[AuditLog]:
    return list(db_session.scalars(select(AuditLog).where(AuditLog.action == action)))


def test_account_create_and_update_write_audit_logs(client, db_session, test_user_id):
    owner = seed_user(db_session, id=UUID(test_user_id))

    create_resp = client.post(
        "/api/v1/accounts/", params={"current_user_id": str(owner.id)}, json={"name": "Audit Account"}
    )
    assert create_resp.status_code == 200, create_resp.text
    account_id = create_resp.json()["id"]

    account_created = _logs_for_action(db_session, "account.created")
    owner_membership_created = _logs_for_action(db_session, "membership.created")

    assert len(account_created) == 1
    assert account_created[0].actor_user_id == owner.id
    assert str(account_created[0].account_id) == account_id
    assert account_created[0].before is None
    assert account_created[0].after["name"] == "Audit Account"

    assert len(owner_membership_created) == 1
    assert owner_membership_created[0].after["role"] == "OWNER"

    update_resp = client.patch(
        f"/api/v1/accounts/{account_id}",
        params={"current_user_id": str(owner.id)},
        json={"name": "Renamed Audit Account"},
    )
    assert update_resp.status_code == 200, update_resp.text

    account_updated = _logs_for_action(db_session, "account.updated")

    assert len(account_updated) == 1
    assert account_updated[0].before["name"] == "Audit Account"
    assert account_updated[0].after["name"] == "Renamed Audit Account"


def test_membership_create_update_and_delete_write_audit_logs(client, db_session):
    owner = seed_user(db_session)
    member = seed_user(db_session)
    account = seed_account(db_session, status=AccountStatus.ACTIVE)
    seed_membership(db_session, user_id=owner.id, account_id=account.id, role=MembershipRole.OWNER)

    create_resp = client.post(
        "/api/v1/memberships/",
        params={"current_user_id": str(owner.id)},
        json={
            "user_id": str(member.id),
            "account_id": str(account.id),
            "role": "MEMBER",
            "default_contribution_share": "0.40",
        },
    )
    assert create_resp.status_code == 200, create_resp.text
    membership_id = create_resp.json()["id"]

    update_resp = client.patch(
        f"/api/v1/memberships/{membership_id}",
        params={"current_user_id": str(owner.id)},
        json={"default_contribution_share": "0.50"},
    )
    assert update_resp.status_code == 200, update_resp.text

    delete_resp = client.delete(f"/api/v1/memberships/{membership_id}", params={"current_user_id": str(owner.id)})
    assert delete_resp.status_code == 204, delete_resp.text

    created = _logs_for_action(db_session, "membership.created")
    updated = _logs_for_action(db_session, "membership.updated")
    deleted = _logs_for_action(db_session, "membership.deleted")

    assert created[0].after["user_id"] == str(member.id)
    assert updated[0].before["default_contribution_share"] == "0.40"
    assert updated[0].after["default_contribution_share"] == "0.50"
    assert deleted[0].before["id"] == membership_id
    assert deleted[0].after is None


def test_expense_create_update_approve_and_delete_write_audit_logs(client, db_session):
    owner = seed_user(db_session)
    account = seed_account(db_session, status=AccountStatus.ACTIVE)
    seed_membership(db_session, user_id=owner.id, account_id=account.id, role=MembershipRole.OWNER)
    category = seed_category(db=db_session, account_id=account.id, name="General", emoji="G")

    create_resp = client.post(
        "/api/v1/expenses/",
        params={"current_user_id": str(owner.id)},
        json={
            "account_id": str(account.id),
            "description": "Audit expense",
            "amount": "12.00",
            "category_id": str(category.id),
            "expense_date": "2026-06-30",
            "currency": "EUR",
            "status": "Completed",
        },
    )
    assert create_resp.status_code == 200, create_resp.text
    expense_id = create_resp.json()["id"]

    update_resp = client.patch(
        f"/api/v1/expenses/{expense_id}", params={"current_user_id": str(owner.id)}, json={"amount": "15.00"}
    )
    assert update_resp.status_code == 200, update_resp.text

    pending_resp = client.post(
        "/api/v1/expenses/",
        params={"current_user_id": str(owner.id)},
        json={
            "account_id": str(account.id),
            "description": "Pending audit expense",
            "amount": "20.00",
            "category_id": str(category.id),
            "expense_date": "2026-06-30",
            "currency": "EUR",
            "status": "Pending",
        },
    )
    assert pending_resp.status_code == 200, pending_resp.text
    pending_id = pending_resp.json()["id"]

    approve_resp = client.patch(f"/api/v1/expenses/{pending_id}/approve", params={"current_user_id": str(owner.id)})
    assert approve_resp.status_code == 200, approve_resp.text

    delete_resp = client.delete(f"/api/v1/expenses/{expense_id}", params={"current_user_id": str(owner.id)})
    assert delete_resp.status_code == 204, delete_resp.text

    created = _logs_for_action(db_session, "expense.created")
    updated = _logs_for_action(db_session, "expense.updated")
    approved = _logs_for_action(db_session, "expense.approved")
    deleted = _logs_for_action(db_session, "expense.deleted")

    assert len(created) == 2
    assert updated[0].before["amount"] == "12.00"
    assert updated[0].after["amount"] == "15.00"
    assert approved[0].before["status"] == "Pending"
    assert approved[0].after["status"] == "Completed"
    assert deleted[0].before["id"] == expense_id


def test_financial_profile_update_writes_audit_log(client, db_session):
    owner = seed_user(db_session)
    account = seed_account(db_session, status=AccountStatus.ACTIVE)
    seed_membership(db_session, user_id=owner.id, account_id=account.id, role=MembershipRole.OWNER)

    resp = client.patch(
        f"/api/v1/accounts/{account.id}/financial-profile",
        params={"current_user_id": str(owner.id)},
        json={"monthly_net_income": "3000.00", "savings_percentage_goal": "20.00"},
    )
    assert resp.status_code == 200, resp.text

    profile_updated = _logs_for_action(db_session, "financial_profile.updated")

    assert len(profile_updated) == 1
    assert profile_updated[0].before is None
    assert profile_updated[0].after["monthly_net_income"] == "3000.00"
    assert profile_updated[0].after["savings_percentage_goal"] == "20.00"
