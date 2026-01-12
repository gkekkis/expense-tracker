import re

import reflex as rx

from ..config import GET_USER_BY_ID_PATH
from ..services.backend_client import ApiError, request
from .app_state import AppState


class AuthState(AppState):
    """Dev auth via UUID stored in browser LocalStorage."""

    user_id: str = rx.LocalStorage(name="user_id")
    user: dict = {}

    user_id_input: str = ""
    error: str = ""

    @rx.var
    def is_logged_in(self) -> bool:
        return bool((self.user_id or "").strip())

    @rx.var
    def user_name(self) -> str:
        return (self.user.get("name") or "").strip()

    def set_user_id_input(self, value: str):
        self.user_id_input = value
        self.error = ""

    def login(self):
        clean = (self.user_id_input or "").strip()
        pattern = r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"

        if not re.match(pattern, clean):
            self.error = "Invalid UUID format."
            return

        self.user_id = clean
        self.user_id_input = ""
        self.error = ""
        return rx.redirect("/")

    def logout(self):
        self.user_id = ""
        self.user = {}
        self.user_id_input = ""
        self.error = ""
        return rx.redirect("/login")

    def require_login(self):
        if not self.is_logged_in:
            return rx.redirect("/login")

    async def load_user(self):
        """Fetch user profile for welcome message."""
        if not self.is_logged_in:
            self.user = {}
            return

        try:
            self.user = request(method="GET", path=f"{GET_USER_BY_ID_PATH}/{self.user_id}", user_id=self.user_id)
        except ApiError:
            # Backend rejected the user → reset local auth
            self.user = {}
            self.user_id = ""
            return rx.redirect("/login")
