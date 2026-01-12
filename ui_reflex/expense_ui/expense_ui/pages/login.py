import reflex as rx

from ..state.auth_state import AuthState


def login_page() -> rx.Component:
    return rx.center(
        rx.card(
            rx.vstack(
                rx.heading("Login (dev)", size="6"),
                rx.text("Paste your UUID. This is our fake auth for now.", color=rx.color("gray", 11), size="2"),
                rx.input(
                    placeholder="Enter your UUID",
                    value=AuthState.user_id_input,
                    on_change=AuthState.set_user_id_input,
                    width="360px",
                ),
                rx.cond(AuthState.error != "", rx.text(AuthState.error, color="red", size="2"), rx.fragment()),
                rx.button("Login", on_click=AuthState.login, width="100%"),
                spacing="3",
                align_items="start",
            ),
            width="420px",
        ),
        min_height="100vh",
    )
