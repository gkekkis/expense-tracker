from __future__ import annotations

import reflex as rx

from ..state.app_state import AppState


def nav_item(label: str, href: str, icon: str) -> rx.Component:
    return rx.link(
        rx.hstack(
            rx.text(icon, font_size="1.05rem", opacity=0.85),
            rx.text(label, font_weight="600"),
            spacing="2",
            align="center",
        ),
        href=href,
        style={
            "width": "100%",
            "padding": "0.6rem 0.7rem",
            "borderRadius": "12px",
            "textDecoration": "none",
            "background": "rgba(255,255,255,0.03)",
            "border": "1px solid rgba(255,255,255,0.06)",
        },
    )


def sidebar() -> rx.Component:
    user_label = rx.cond(AppState.user_name, AppState.user_name, "User")
    account_label = rx.cond(AppState.account_name, AppState.account_name, "No account")

    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.text("💸", font_size="1.4rem"),
                rx.text("Expense Tracker", font_weight="800"),
                spacing="2",
                align="center",
            ),
            rx.divider(opacity=0.2),
            rx.vstack(
                nav_item("Accounts", "/accounts", "🏠"),
                nav_item("Overview", "/overview", "✨"),
                nav_item("Expenses", "/expenses", "🧾"),
                nav_item("Recurring", "/recurring", "🔁"),
                nav_item("Members", "/members", "👥"),
                nav_item("Budget", "/budget", "📊"),
                nav_item("Settings", "/settings", "⚙️"),
                spacing="2",
                width="100%",
            ),
            rx.spacer(),
            rx.box(
                rx.vstack(
                    rx.hstack(
                        rx.badge(user_label), rx.badge(account_label, variant="surface"), spacing="2", wrap="wrap"
                    ),
                    rx.button("Sign out", variant="surface", width="100%", on_click=AppState.sign_out),
                    spacing="2",
                    width="100%",
                ),
                width="100%",
                padding="0.8rem",
                border_radius="16px",
                border="1px solid rgba(255,255,255,0.08)",
                background="rgba(255,255,255,0.03)",
            ),
            spacing="3",
            width="100%",
            height="100%",
        ),
        width="280px",
        min_width="280px",
        height="100vh",
        padding="1rem",
        position="sticky",
        top="0",
        border_right="1px solid rgba(255,255,255,0.06)",
        background="rgba(10, 10, 14, 0.6)",
        backdrop_filter="blur(12px)",
    )


def topbar() -> rx.Component:
    # Show the active account in the top bar too.
    account_label = rx.cond(AppState.account_name, AppState.account_name, "Select an account")
    user_label = rx.cond(AppState.user_name, AppState.user_name, "User")

    return rx.hstack(
        rx.hstack(
            rx.text("✨", font_size="1.1rem"), rx.text(account_label, font_weight="700"), spacing="2", align="center"
        ),
        rx.spacer(),
        rx.hstack(rx.badge(user_label, variant="surface"), spacing="2", align="center"),
        width="100%",
        padding="0.75rem 1rem",
        border_bottom="1px solid rgba(255,255,255,0.06)",
        background="rgba(10, 10, 14, 0.45)",
        backdrop_filter="blur(10px)",
        position="sticky",
        top="0",
        z_index="10",
    )


def shell(content: rx.Component) -> rx.Component:
    return rx.hstack(
        sidebar(),
        rx.box(topbar(), rx.box(content, padding="1.25rem"), width="100%"),
        width="100%",
        min_height="100vh",
        background=(
            "radial-gradient(1200px 600px at 20% 0%, rgba(125, 211, 252, 0.12), transparent 60%), "
            "radial-gradient(900px 600px at 90% 20%, rgba(167, 139, 250, 0.10), transparent 55%), "
            "rgba(8, 8, 12, 1)"
        ),
        color="white",
    )
