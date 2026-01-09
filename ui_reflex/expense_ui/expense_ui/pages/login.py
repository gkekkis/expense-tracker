# ui_reflex/expense_ui/expense_ui/pages/login.py
import reflex as rx

from ..state.auth_state import AuthState


def login_page() -> rx.Component:
    return rx.center(
        rx.card(
            rx.vstack(
                rx.heading("Login (dev)", size="6"),
                rx.text("Enter a User UUID. This will be sent as X-User-Id to the backend later.", color_scheme="gray"),
                rx.input(
                    placeholder="e.g. 2f1c9b1e-7c2b-4f9e-9d6e-4a7d5d2c1a0b",
                    value=AuthState.user_id_input,
                    on_change=AuthState.set_user_id_input,
                    width="100%",
                ),
                rx.cond(AuthState.error != "", rx.text(AuthState.error, color="red", size="2")),
                rx.button("Continue", on_click=AuthState.login, width="100%"),
                spacing="3",
                width="420px",
            ),
            width="min(520px, 95vw)",
        ),
        min_height="100vh",
        padding="24px",
    )
