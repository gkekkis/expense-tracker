from __future__ import annotations

import reflex as rx

from ..components.layout import shell
from ..state.app_state import AppState


@rx.page(route="/overview", title="Expense Tracker · Overview")
def overview_page() -> rx.Component:
    title_text = rx.cond(AppState.account_name, AppState.account_name, "Overview")

    content = rx.vstack(
        rx.hstack(
            rx.text(title_text, font_size="1.8rem", font_weight="900"),
            rx.spacer(),
            rx.button("Refresh", variant="surface", on_click=AppState.load_budget),
            spacing="2",
            width="100%",
            align="center",
        ),
        rx.text("Your account snapshot: budget health, quick actions, and recent activity.", opacity=0.7),
        rx.divider(opacity=0.25),
        # Guard if no account is selected
        rx.cond(
            AppState.has_account,
            rx.vstack(
                rx.hstack(
                    rx.box(
                        rx.vstack(
                            rx.text("Budget status", font_weight="800"),
                            rx.text(rx.cond(AppState.budget, "Loaded", "Not loaded yet"), opacity=0.7),
                            spacing="1",
                            align="start",
                        ),
                        padding="1rem",
                        border_radius="18px",
                        border="1px solid rgba(255,255,255,0.10)",
                        background="rgba(255,255,255,0.04)",
                        backdrop_filter="blur(10px)",
                        width="100%",
                    ),
                    rx.box(
                        rx.vstack(
                            rx.text("Quick actions", font_weight="800"),
                            rx.hstack(
                                rx.link(rx.button("Add expense", width="100%"), href="/expenses"),
                                rx.link(rx.button("Members", variant="surface", width="100%"), href="/members"),
                                spacing="2",
                                width="100%",
                            ),
                            spacing="2",
                            align="start",
                        ),
                        padding="1rem",
                        border_radius="18px",
                        border="1px solid rgba(255,255,255,0.10)",
                        background="rgba(255,255,255,0.04)",
                        backdrop_filter="blur(10px)",
                        width="100%",
                    ),
                    spacing="3",
                    width="100%",
                    flex_wrap="wrap",
                ),
                spacing="3",
                width="100%",
            ),
            rx.box(rx.text("Pick an account first (Accounts page).", opacity=0.8), padding="1rem"),
        ),
        spacing="3",
        width="100%",
    )

    # On mount, load account context and budget.
    # These will no-op if user_id/account_id isn't set.
    return shell(rx.box(content, on_mount=[AppState.load_memberships, AppState.load_categories, AppState.load_budget]))
