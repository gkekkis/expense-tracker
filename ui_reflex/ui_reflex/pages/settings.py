from __future__ import annotations

import os

import reflex as rx

from ..components.layout import shell
from ..state.app_state import AppState


@rx.page(route="/settings", title="Expense Tracker · Settings")
def settings_page() -> rx.Component:
    api_base = os.getenv("API_BASE_URL", "http://127.0.0.1:8001")

    user_line = rx.cond(
        AppState.has_user,
        rx.text(rx.fragment("User: ", AppState.user_name, " (", AppState.user_id, ")"), opacity=0.75),
        rx.text("No user selected", opacity=0.75),
    )

    account_line = rx.cond(
        AppState.has_account,
        rx.text(rx.fragment("Account: ", AppState.account_name, " (", AppState.account_id, ")"), opacity=0.75),
        rx.text("No account selected", opacity=0.75),
    )

    content = rx.vstack(
        rx.text("Settings", font_size="1.8rem", font_weight="900"),
        rx.text("Small switches that keep the app convenient for daily use.", opacity=0.75),
        rx.divider(opacity=0.25),
        rx.grid(
            rx.box(
                rx.vstack(
                    rx.text("Session", font_weight="800"),
                    user_line,
                    account_line,
                    rx.button("Sign out", on_click=AppState.sign_out, width="100%"),
                    spacing="2",
                    width="100%",
                ),
                padding="1rem",
                border_radius="18px",
                border="1px solid rgba(255,255,255,0.10)",
                background="rgba(255,255,255,0.04)",
            ),
            rx.box(
                rx.vstack(
                    rx.text("Developer", font_weight="800"),
                    rx.text(rx.fragment("API_BASE_URL: ", api_base), opacity=0.75),
                    rx.text("Auth uses X-User-Id header. No tokens.", opacity=0.75),
                    rx.text("Tip: if you run Reflex on another port, enable CORS on FastAPI.", opacity=0.75),
                    spacing="2",
                    width="100%",
                ),
                padding="1rem",
                border_radius="18px",
                border="1px solid rgba(255,255,255,0.10)",
                background="rgba(255,255,255,0.03)",
            ),
            columns="1fr 2fr",
            gap="1rem",
            width="100%",
        ),
        spacing="4",
        width="100%",
    )
    return shell(content)
