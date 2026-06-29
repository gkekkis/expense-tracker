from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any, Dict, List, Optional

import reflex as rx

from ..api import ApiError, request


def _today_iso() -> str:
    return date.today().isoformat()


@dataclass
class Toast:
    kind: str  # 'success' | 'error' | 'info'
    message: str


class AppState(rx.State):
    """
    Single app state for MVP.

    Keeps auth + selected account + page data.
    """

    # Auth/session
    user_id: str = ""
    user_name: str = ""

    # Navigation context
    account_id: str = ""
    account_name: str = ""
    membership_role: str = ""  # OWNER/MEMBER/VIEWER

    # Global UI
    is_loading: bool = False
    toast: Optional[Toast] = None

    # Users
    users: List[Dict[str, Any]] = []
    new_user_name: str = ""
    new_user_email: str = ""

    # Accounts
    accounts: List[Dict[str, Any]] = []
    new_account_name: str = ""

    # Categories (current account)
    categories: List[Dict[str, Any]] = []

    # Expenses search
    expenses: List[Dict[str, Any]] = []
    expenses_total_count: int = 0
    expenses_total_amount_formatted: str = ""
    expenses_limit: int = 20
    expenses_offset: int = 0

    # Expense form
    exp_description: str = ""
    exp_amount: str = ""
    exp_category_id: str = ""
    exp_date: str = _today_iso()
    exp_currency: str = "EUR"
    exp_status: str = "Completed"
    exp_personal_factor: str = ""  # 0..1 string

    # Filters
    f_status_pending: bool = True
    f_status_completed: bool = True
    f_status_cancelled: bool = False
    f_start_date: str = ""
    f_end_date: str = ""
    f_category_id: str = ""
    f_search_query: str = ""
    f_min_amount: str = ""
    f_max_amount: str = ""
    target_currency: str = "EUR"

    # Members
    memberships: List[Dict[str, Any]] = []
    add_member_user_id: str = ""
    add_member_role: str = "MEMBER"

    # Recurring templates
    recurring_templates: List[Dict[str, Any]] = []

    # Budget
    budget: Dict[str, Any] = {}

    # Financial profile
    profile: Dict[str, Any] = {}
    profile_monthly_income: str = ""
    profile_savings_goal: str = ""
    profile_emergency_target: str = ""

    # --------------------------
    # Explicit setters (Reflex >=0.8.24: avoids deprecation warnings)
    # --------------------------
    def set_new_user_name(self, v: str):
        self.new_user_name = v

    def set_new_user_email(self, v: str):
        self.new_user_email = v

    def set_new_account_name(self, v: str):
        self.new_account_name = v

    def set_f_status_pending(self, v: bool):
        self.f_status_pending = v

    def set_f_status_completed(self, v: bool):
        self.f_status_completed = v

    def set_f_status_cancelled(self, v: bool):
        self.f_status_cancelled = v

    def set_f_start_date(self, v: str):
        self.f_start_date = v

    def set_f_end_date(self, v: str):
        self.f_end_date = v

    def set_f_category_id(self, v: str):
        self.f_category_id = v

    def set_f_search_query(self, v: str):
        self.f_search_query = v

    def set_f_min_amount(self, v: str):
        self.f_min_amount = v

    def set_f_max_amount(self, v: str):
        self.f_max_amount = v

    def set_add_member_role(self, v: str):
        self.add_member_role = v

    def set_target_currency(self, v: str):
        self.target_currency = v

    def set_exp_description(self, v: str):
        self.exp_description = v

    def set_exp_amount(self, v: str):
        self.exp_amount = v

    def set_exp_date(self, v: str):
        self.exp_date = v

    def set_exp_status(self, v: str):
        self.exp_status = v

    def set_exp_personal_factor(self, v: str):
        self.exp_personal_factor = v

    def set_exp_currency(self, v: str):
        self.exp_currency = v

    def set_profile_monthly_income(self, v: str):
        self.profile_monthly_income = v

    def set_profile_savings_goal(self, v: str):
        self.profile_savings_goal = v

    def set_profile_emergency_target(self, v: str):
        self.profile_emergency_target = v

    # ----- helpers -----
    def set_toast(self, kind: str, message: str):
        self.toast = Toast(kind=kind, message=message)

    def clear_toast(self):
        self.toast = None

    @rx.var
    def has_user(self) -> bool:
        return bool(self.user_id)

    @rx.var
    def has_account(self) -> bool:
        return bool(self.account_id)

    @rx.var
    def is_owner(self) -> bool:
        return self.membership_role == "OWNER"

    @rx.var
    def is_viewer(self) -> bool:
        return self.membership_role == "VIEWER"

    # --------------------------
    # Select helpers (must be Vars, cannot build lists in pages)
    # --------------------------
    @rx.var
    def user_select_items(self) -> List[str]:
        """Strings shown in the members 'Add member' dropdown."""
        items: List[str] = []
        for u in self.users:
            name = u.get("name") or "Unknown"
            email = u.get("email") or ""
            label = f"{name} · {email}" if email else name
            # encode id into item; we'll parse it on change
            items.append(f"{label}|||{u.get('id')}")
        return items

    @rx.var
    def user_selected_item(self) -> str:
        """Derive current select value from add_member_user_id."""
        if not self.add_member_user_id:
            return ""
        # find matching encoded item
        for u in self.users:
            if u.get("id") == self.add_member_user_id:
                name = u.get("name") or "Unknown"
                email = u.get("email") or ""
                label = f"{name} · {email}" if email else name
                return f"{label}|||{u.get('id')}"
        return ""

    def set_add_member_user_item(self, item: str):
        """Called by members page select."""
        # item format: "Label|||<uuid>"
        if not item:
            self.add_member_user_id = ""
            return
        if "|||" in item:
            self.add_member_user_id = item.split("|||", 1)[1]
        else:
            # fallback: if only id is passed
            self.add_member_user_id = item

    # ----- auth -----
    async def load_users(self):
        self.is_loading = True
        self.clear_toast()
        try:
            self.users = await request("GET", "/api/v1/users/")
        except ApiError as e:
            self.set_toast("error", f"Failed to load users: {e.detail}")
        finally:
            self.is_loading = False

    def pick_user(self, user_id: str, user_name: str):
        self.user_id = user_id
        self.user_name = user_name
        self.account_id = ""
        self.account_name = ""
        self.membership_role = ""
        return rx.redirect("/accounts")

    async def create_user(self):
        if not self.new_user_name.strip() or not self.new_user_email.strip():
            self.set_toast("error", "Name and email are required")
            return
        self.is_loading = True
        self.clear_toast()
        try:
            user = await request(
                "POST",
                "/api/v1/users/",
                json={"name": self.new_user_name.strip(), "email": self.new_user_email.strip(), "status": "ACTIVE"},
            )
            self.set_toast("success", "User created")
            self.new_user_name = ""
            self.new_user_email = ""
            # Auto sign-in
            self.user_id = user["id"]
            self.user_name = user["name"]
            return rx.redirect("/accounts")
        except ApiError as e:
            self.set_toast("error", f"Create user failed: {e.detail}")
        finally:
            self.is_loading = False

    def sign_out(self):
        self.user_id = ""
        self.user_name = ""
        self.account_id = ""
        self.account_name = ""
        self.membership_role = ""
        return rx.redirect("/")

    # ----- accounts -----
    async def load_accounts(self):
        if not self.user_id:
            return
        self.is_loading = True
        self.clear_toast()
        try:
            self.accounts = await request("GET", "/api/v1/users/me/accounts", user_id=self.user_id)
        except ApiError as e:
            self.set_toast("error", f"Failed to load accounts: {e.detail}")
        finally:
            self.is_loading = False

    def clear_new_account(self):
        self.new_account_name = ""

    async def pick_account(self, account_id: str, account_name: str):
        """Select an account from the UI and enter it safely (async)."""
        self.is_loading = True
        self.clear_toast()
        try:
            await self.enter_account(account_id, account_name)
            return rx.redirect("/overview")
        except ApiError as e:
            self.set_toast("error", f"Failed to enter account: {e.detail}")
        finally:
            self.is_loading = False

    async def enter_and_go(self, account_id: str, account_name: str):
        await self.enter_account(account_id, account_name)
        return rx.redirect("/overview")

    async def create_account(self):
        if not self.new_account_name.strip():
            self.set_toast("error", "Account name is required")
            return
        self.is_loading = True
        self.clear_toast()
        try:
            acct = await request(
                "POST",
                "/api/v1/accounts/",
                user_id=self.user_id,
                json={"name": self.new_account_name.strip(), "status": "ACTIVE"},
            )
            self.set_toast("success", "Account created")
            self.new_account_name = ""
            await self.load_accounts()
            await self.enter_account(acct["id"], acct["name"])
            return rx.redirect("/overview")
        except ApiError as e:
            self.set_toast("error", f"Create account failed: {e.detail}")
        finally:
            self.is_loading = False

    async def enter_account(self, account_id: str, account_name: str):
        self.account_id = account_id
        self.account_name = account_name
        await self.load_memberships()
        await self.load_categories()

    async def load_categories(self):
        if not (self.user_id and self.account_id):
            return
        try:
            self.categories = await request(
                "GET", f"/api/v1/accounts/{self.account_id}/categories", user_id=self.user_id
            )
        except ApiError:
            self.categories = []

    # ----- memberships -----
    async def load_memberships(self):
        if not (self.user_id and self.account_id):
            return
        self.is_loading = True
        self.clear_toast()
        try:
            self.memberships = await request(
                "GET", f"/api/v1/accounts/{self.account_id}/memberships", user_id=self.user_id
            )
            self.membership_role = ""
            for m in self.memberships:
                if m.get("user_id") == self.user_id:
                    self.membership_role = m.get("role", "")
                    break
        except ApiError as e:
            self.set_toast("error", f"Failed to load members: {e.detail}")
        finally:
            self.is_loading = False

    async def add_member(self):
        if not self.account_id:
            self.set_toast("error", "Pick an account first")
            return
        if not self.add_member_user_id:
            self.set_toast("error", "Select a user")
            return
        self.is_loading = True
        self.clear_toast()
        try:
            await request(
                "POST",
                "/api/v1/memberships/",
                user_id=self.user_id,
                json={"user_id": self.add_member_user_id, "account_id": self.account_id, "role": self.add_member_role},
            )
            self.set_toast("success", "Member added")
            self.add_member_user_id = ""
            await self.load_memberships()
        except ApiError as e:
            self.set_toast("error", f"Add member failed: {e.detail}")
        finally:
            self.is_loading = False

    async def update_membership(self, membership_id: str, role: str | None = None, share: str | None = None):
        self.is_loading = True
        self.clear_toast()
        body: Dict[str, Any] = {}
        if role is not None:
            body["role"] = role
        if share is not None and share != "":
            body["default_contribution_share"] = share
        try:
            await request("PATCH", f"/api/v1/memberships/{membership_id}", user_id=self.user_id, json=body)
            self.set_toast("success", "Membership updated")
            await self.load_memberships()
        except ApiError as e:
            self.set_toast("error", f"Update membership failed: {e.detail}")
        finally:
            self.is_loading = False

    async def delete_membership(self, membership_id: str):
        self.is_loading = True
        self.clear_toast()
        try:
            await request("DELETE", f"/api/v1/memberships/{membership_id}", user_id=self.user_id)
            self.set_toast("success", "Member removed")
            await self.load_memberships()
        except ApiError as e:
            self.set_toast("error", f"Remove member failed: {e.detail}")
        finally:
            self.is_loading = False

    # ----- expenses -----
    def _selected_statuses(self) -> List[str]:
        statuses: List[str] = []
        if self.f_status_pending:
            statuses.append("Pending")
        if self.f_status_completed:
            statuses.append("Completed")
        if self.f_status_cancelled:
            statuses.append("Cancelled")
        return statuses

    async def search_expenses(self, reset_offset: bool = False):
        if not (self.user_id and self.account_id):
            return
        if reset_offset:
            self.expenses_offset = 0
        self.is_loading = True
        self.clear_toast()

        body: Dict[str, Any] = {
            "account_id": self.account_id,
            "limit": self.expenses_limit,
            "offset": self.expenses_offset,
        }
        statuses = self._selected_statuses()
        if statuses:
            body["status"] = statuses
        if self.f_start_date:
            body["start_date"] = self.f_start_date
        if self.f_end_date:
            body["end_date"] = self.f_end_date
        if self.f_category_id:
            body["category_id"] = self.f_category_id
        if self.f_search_query:
            body["search_query"] = self.f_search_query
        if self.f_min_amount:
            body["min_amount"] = float(self.f_min_amount)
        if self.f_max_amount:
            body["max_amount"] = float(self.f_max_amount)

        try:
            resp = await request(
                "POST",
                "/api/v1/expenses/search",
                user_id=self.user_id,
                params={"target_currency": self.target_currency},
                json=body,
            )
            self.expenses = resp.get("items", [])
            self.expenses_total_count = resp.get("total_count", 0)
            self.expenses_total_amount_formatted = resp.get("total_amount_formatted", "")
        except ApiError as e:
            self.set_toast("error", f"Search failed: {e.detail}")
        finally:
            self.is_loading = False

    async def next_page(self):
        if self.expenses_offset + self.expenses_limit >= self.expenses_total_count:
            return
        self.expenses_offset += self.expenses_limit
        await self.search_expenses(reset_offset=False)

    async def prev_page(self):
        self.expenses_offset = max(0, self.expenses_offset - self.expenses_limit)
        await self.search_expenses(reset_offset=False)

    async def create_expense(self):
        if self.is_viewer:
            self.set_toast("error", "Viewers can’t create expenses")
            return
        if not (self.account_id and self.exp_description.strip() and self.exp_amount.strip() and self.exp_category_id):
            self.set_toast("error", "Description, amount, and category are required")
            return

        body: Dict[str, Any] = {
            "account_id": self.account_id,
            "description": self.exp_description.strip(),
            "amount": self.exp_amount.strip(),
            "category_id": self.exp_category_id,
            "expense_date": self.exp_date or _today_iso(),
            "currency": self.exp_currency,
            "status": self.exp_status,
        }
        if self.exp_personal_factor.strip() != "":
            body["personal_responsibility_factor"] = self.exp_personal_factor.strip()

        self.is_loading = True
        self.clear_toast()
        try:
            await request("POST", "/api/v1/expenses/", user_id=self.user_id, json=body)
            self.set_toast("success", "Expense added")
            self.exp_description = ""
            self.exp_amount = ""
            self.exp_personal_factor = ""
            await self.search_expenses(reset_offset=True)
        except ApiError as e:
            self.set_toast("error", f"Create expense failed: {e.detail}")
        finally:
            self.is_loading = False

    async def approve_expense(self, expense_id: str):
        self.is_loading = True
        self.clear_toast()
        try:
            await request("PATCH", f"/api/v1/expenses/{expense_id}/approve", user_id=self.user_id)
            self.set_toast("success", "Approved")
            await self.search_expenses(reset_offset=False)
        except ApiError as e:
            self.set_toast("error", f"Approve failed: {e.detail}")
        finally:
            self.is_loading = False

    async def delete_expense(self, expense_id: str):
        self.is_loading = True
        self.clear_toast()
        try:
            await request("DELETE", f"/api/v1/expenses/{expense_id}", user_id=self.user_id)
            self.set_toast("success", "Deleted")
            await self.search_expenses(reset_offset=False)
        except ApiError as e:
            self.set_toast("error", f"Delete failed: {e.detail}")
        finally:
            self.is_loading = False

    # ----- recurring -----
    async def load_recurring_templates(self):
        if not (self.user_id and self.account_id):
            return
        self.is_loading = True
        self.clear_toast()
        try:
            self.recurring_templates = await request(
                "GET", f"/api/v1/accounts/{self.account_id}/recurring-templates", user_id=self.user_id
            )
        except ApiError as e:
            self.set_toast("error", f"Failed to load templates: {e.detail}")
        finally:
            self.is_loading = False

    # ----- budget/profile -----
    async def load_budget(self):
        if not (self.user_id and self.account_id):
            return
        self.is_loading = True
        self.clear_toast()
        try:
            params: Dict[str, Any] = {"account_id": self.account_id}
            statuses = self._selected_statuses()
            if statuses:
                params["status"] = statuses
            if self.f_start_date:
                params["start_date"] = self.f_start_date
            if self.f_end_date:
                params["end_date"] = self.f_end_date
            if self.f_category_id:
                params["category_id"] = self.f_category_id
            if self.f_search_query:
                params["search_query"] = self.f_search_query
            if self.f_min_amount:
                params["min_amount"] = float(self.f_min_amount)
            if self.f_max_amount:
                params["max_amount"] = float(self.f_max_amount)

            self.budget = await request("GET", "/api/v1/summaries/budget-status", user_id=self.user_id, params=params)
        except ApiError as e:
            self.set_toast("error", f"Budget failed: {e.detail}")
        finally:
            self.is_loading = False

    async def load_profile(self):
        if not (self.user_id and self.account_id):
            return
        self.is_loading = True
        self.clear_toast()
        try:
            prof = await request("GET", f"/api/v1/accounts/{self.account_id}/financial-profile", user_id=self.user_id)
            self.profile = prof or {}
            self.profile_monthly_income = str(self.profile.get("monthly_net_income", ""))
            self.profile_savings_goal = str(self.profile.get("savings_percentage_goal", ""))
            self.profile_emergency_target = str(self.profile.get("emergency_fund_target", ""))
        except ApiError as e:
            self.set_toast("error", f"Profile load failed: {e.detail}")
        finally:
            self.is_loading = False

    async def save_profile(self):
        if not self.is_owner:
            self.set_toast("error", "Only owners can update the financial profile")
            return
        self.is_loading = True
        self.clear_toast()
        try:
            payload: Dict[str, Any] = {}
            if self.profile_monthly_income.strip() != "":
                payload["monthly_net_income"] = self.profile_monthly_income.strip()
            if self.profile_savings_goal.strip() != "":
                payload["savings_percentage_goal"] = self.profile_savings_goal.strip()
            if self.profile_emergency_target.strip() != "":
                payload["emergency_fund_target"] = self.profile_emergency_target.strip()

            self.profile = await request(
                "PATCH", f"/api/v1/accounts/{self.account_id}/financial-profile", user_id=self.user_id, json=payload
            )
            self.set_toast("success", "Profile updated")
        except ApiError as e:
            self.set_toast("error", f"Save failed: {e.detail}")
        finally:
            self.is_loading = False
        # --------------------------

    # Category select helpers (for Expenses filters)
    # --------------------------
    @rx.var
    def category_select_items(self) -> List[str]:
        """
        Strings shown in the category dropdown.

        Encodes id into item as: "<name>|||<uuid>"
        """
        items: List[str] = []
        for c in self.categories:
            name = c.get("name") or "Uncategorized"
            cid = c.get("id") or ""
            items.append(f"{name}|||{cid}")
        return items

    @rx.var
    def category_selected_item(self) -> str:
        """Derive current select value from f_category_id."""
        if not self.f_category_id:
            return ""
        for c in self.categories:
            if c.get("id") == self.f_category_id:
                name = c.get("name") or "Uncategorized"
                return f"{name}|||{c.get('id')}"
        return ""

    def set_category_item(self, item: str):
        """Called by expenses filter select to set f_category_id."""
        if not item:
            self.f_category_id = ""
            return
        if "|||" in item:
            self.f_category_id = item.split("|||", 1)[1]
        else:
            self.f_category_id = item

    @rx.var
    def exp_category_selected_item(self) -> str:
        """Derive current select value from exp_category_id."""
        if not self.exp_category_id:
            return ""
        for c in self.categories:
            if c.get("id") == self.exp_category_id:
                name = c.get("name") or "Uncategorized"
                return f"{name}|||{c.get('id')}"
        return ""

    def set_exp_category_item(self, item: str):
        """Called by the Quick Add category select to set exp_category_id."""
        if not item:
            self.exp_category_id = ""
            return
        if "|||" in item:
            self.exp_category_id = item.split("|||", 1)[1]
        else:
            self.exp_category_id = item
