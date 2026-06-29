from __future__ import annotations

import reflex as rx

from ..components.layout import shell
from ..state.app_state import AppState


def _account_card(a) -> rx.Component:
    """Account tile rendered inside rx.foreach; `a` is Var-like."""
    name = rx.cond(a["name"], a["name"], "Untitled")
    status = rx.cond(a["status"], a["status"], "ACTIVE")

    return rx.button(
        rx.vstack(
            rx.hstack(
                rx.text("🏠", font_size="1.25rem"),
                rx.text(name, font_weight="800"),
                rx.spacer(),
                rx.badge(status, variant="surface"),
                width="100%",
                align="center",
            ),
            rx.text("Open account", opacity=0.7, size="2"),
            spacing="2",
            width="100%",
            align="start",
        ),
        on_click=AppState.pick_account(a["id"], name),
        width="100%",
        variant="surface",
        style={
            "padding": "1rem",
            "borderRadius": "18px",
            "border": "1px solid rgba(255,255,255,0.10)",
            "background": "rgba(255,255,255,0.04)",
            "backdropFilter": "blur(10px)",
            "textAlign": "left",
        },
    )


@rx.page(route="/accounts", title="Expense Tracker · Accounts")
def accounts_page() -> rx.Component:
    content = rx.vstack(
        rx.hstack(
            rx.vstack(
                rx.text("Accounts", font_size="2rem", font_weight="900"),
                rx.text("Pick an account or create a new one.", opacity=0.7),
                spacing="1",
                align="start",
            ),
            rx.spacer(),
            rx.button("Refresh", on_click=AppState.load_accounts, variant="surface"),
            width="100%",
            align="center",
        ),
        rx.divider(opacity=0.25),
        # Create account
        rx.box(
            rx.vstack(
                rx.text("Create account", font_weight="800"),
                rx.input(
                    placeholder="Account name", value=AppState.new_account_name, on_change=AppState.set_new_account_name
                ),
                rx.button("Create", on_click=AppState.create_account, width="100%"),
                spacing="2",
                width="100%",
            ),
            padding="1rem",
            border_radius="18px",
            border="1px solid rgba(255,255,255,0.10)",
            background="rgba(255,255,255,0.04)",
            backdrop_filter="blur(10px)",
            width="100%",
        ),
        rx.divider(opacity=0.25),
        # Accounts grid (CSS grid: most compatible across Reflex versions)
        rx.cond(
            AppState.accounts,
            rx.box(
                rx.foreach(AppState.accounts, _account_card),
                style={
                    "display": "grid",
                    "gridTemplateColumns": "repeat(auto-fit, minmax(260px, 1fr))",
                    "gap": "12px",
                    "width": "100%",
                },
            ),
            rx.box(rx.text("No accounts yet. Create one above.", opacity=0.75), padding="1rem"),
        ),
        spacing="4",
        width="100%",
    )

    return shell(rx.box(content, on_mount=AppState.load_accounts))
