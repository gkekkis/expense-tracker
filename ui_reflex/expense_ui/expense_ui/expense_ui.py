# ui_reflex/expense_ui/expense_ui/expense_ui.py
import reflex as rx

from .pages.login import login_page
from .state.auth_state import AuthState


def index_page() -> rx.Component:
    return rx.vstack(
        rx.hstack(
            rx.heading("Expense Tracker", size="6"),
            rx.spacer(),
            rx.button("Logout", variant="outline", on_click=AuthState.logout),
            width="100%",
        ),
        rx.text("✅ You are logged in. Next we will fetch accounts from your backend."),
        padding="24px",
        max_width="900px",
        margin="0 auto",
    )


app = rx.App(theme=rx.theme(appearance="dark", has_background=True, radius="large", accent_color="grass"))

# Public page
app.add_page(login_page, route="/login", title="Login")

# Protected page: guard runs on page load
app.add_page(index_page, route="/", title="Expense Tracker", on_load=AuthState.require_login)
