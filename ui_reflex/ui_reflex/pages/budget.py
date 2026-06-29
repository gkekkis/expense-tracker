from __future__ import annotations

import reflex as rx

from ..components.layout import shell
from ..state.app_state import AppState


@rx.page(route="/budget", title="Expense Tracker · Budget", on_load=[AppState.load_budget, AppState.load_profile])
def budget_page() -> rx.Component:
    budget_card = rx.box(
        rx.vstack(
            rx.text("Budget status", font_weight="900", font_size="1.4rem"),
            rx.text("Server-computed totals based on your filters.", opacity=0.75),
            rx.divider(opacity=0.25),
            rx.hstack(
                rx.box(
                    rx.text("Income", opacity=0.7), rx.text(AppState.budget.get("total_income", "—"), font_weight="900")
                ),
                rx.spacer(),
                rx.box(
                    rx.text("Spent", opacity=0.7), rx.text(AppState.budget.get("total_spent", "—"), font_weight="900")
                ),
                rx.spacer(),
                rx.box(
                    rx.text("Remaining", opacity=0.7),
                    rx.text(AppState.budget.get("remaining_budget", "—"), font_weight="900"),
                ),
                width="100%",
            ),
            rx.box(
                rx.text(f"Health: {AppState.budget.get('health_percentage', '—')}%", font_weight="800"),
                padding_top="0.5rem",
            ),
            rx.button("Refresh", on_click=AppState.load_budget, width="100%"),
            spacing="3",
            width="100%",
        ),
        padding="1rem",
        border_radius="18px",
        border="1px solid rgba(255,255,255,0.10)",
        background="rgba(255,255,255,0.04)",
    )

    profile_card = rx.box(
        rx.vstack(
            rx.hstack(
                rx.text("Financial profile", font_weight="900", font_size="1.4rem"),
                rx.spacer(),
                rx.cond(
                    AppState.is_owner,
                    rx.badge("OWNER can edit", variant="outline"),
                    rx.badge("Read-only", variant="soft"),
                ),
                width="100%",
                align="center",
            ),
            rx.text("Used by budget health. Stored per account.", opacity=0.75),
            rx.divider(opacity=0.25),
            rx.input(
                placeholder="Monthly net income",
                value=AppState.profile_monthly_income,
                on_change=AppState.set_profile_monthly_income,
                disabled=~AppState.is_owner,
            ),
            rx.input(
                placeholder="Savings goal %",
                value=AppState.profile_savings_goal,
                on_change=AppState.set_profile_savings_goal,
                disabled=~AppState.is_owner,
            ),
            rx.input(
                placeholder="Emergency fund target",
                value=AppState.profile_emergency_target,
                on_change=AppState.set_profile_emergency_target,
                disabled=~AppState.is_owner,
            ),
            rx.button("Save", on_click=AppState.save_profile, disabled=~AppState.is_owner, width="100%"),
            spacing="3",
            width="100%",
        ),
        padding="1rem",
        border_radius="18px",
        border="1px solid rgba(255,255,255,0.10)",
        background="rgba(255,255,255,0.03)",
    )

    content = rx.vstack(
        rx.text("Budget", font_size="1.8rem", font_weight="900"),
        rx.text("A quick health score that stays honest across currencies.", opacity=0.75),
        rx.divider(opacity=0.25),
        rx.grid(
            budget_card, profile_card, columns=rx.breakpoints(initial="1fr", md="1fr 2fr"), gap="1rem", width="100%"
        ),
        spacing="4",
        width="100%",
    )
    return shell(content)
