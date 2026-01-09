import re

import reflex as rx


class AuthState(rx.State):
    user_id: str = rx.LocalStorage(name="user_id")
    user_id_input: str = ""
    error: str = ""

    @rx.var
    def is_logged_in(self) -> bool:
        return bool((self.user_id or "").strip())

    def set_user_id_input(self, value: str):
        self.user_id_input = value
        self.error = ""

    def login(self):
        clean = (self.user_id_input or "").strip()
        pattern = r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"

        if not re.match(pattern, clean):
            self.error = "Invalid ID format. Please enter a valid UUID."
            return

        self.user_id = clean
        self.user_id_input = ""
        self.error = ""
        return rx.redirect("/")

    def logout(self):
        self.user_id = ""
        self.user_id_input = ""
        self.error = ""
        return rx.redirect("/login")

    def require_login(self):
        """Use this in on_load for protected pages."""
        if not self.is_logged_in:
            return rx.redirect("/login")
