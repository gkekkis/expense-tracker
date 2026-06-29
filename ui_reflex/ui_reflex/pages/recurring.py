from __future__ import annotations

import reflex as rx

from ..components.layout import shell
from ..state.app_state import AppState


def _template_card(t) -> rx.Component:
    name = rx.cond(t.get("name"), t.get("name"), "Untitled")
    desc = rx.cond(t.get("description"), t.get("description"), "")
    amt = rx.cond(t.get("amount"), t.get("amount"), "0.00")
    cur = rx.cond(t.get("currency"), t.get("currency"), "")
    freq = rx.cond(t.get("frequency"), t.get("frequency"), "")
    next_dt = rx.cond(t.get("next_occurrence_date"), t.get("next_occurrence_date"), "")
    icon = rx.cond(t.get("icon"), t.get("icon"), "R")

    return rx.box(
        rx.hstack(
            rx.hstack(
                rx.text(icon, font_size="1.6rem"),
                rx.vstack(
                    rx.text(name, font_weight="900"),
                    rx.cond(desc, rx.text(desc, opacity=0.75, size="2"), rx.fragment()),
                    rx.hstack(
                        rx.badge(freq, variant="surface"),
                        rx.text(f"Next: {next_dt}", opacity=0.75, size="2"),
                        spacing="2",
                        align="center",
                    ),
                    spacing="1",
                    align="start",
                ),
                spacing="3",
                align="start",
            ),
            rx.spacer(),
            rx.vstack(rx.text(amt, font_weight="900"), rx.text(cur, opacity=0.7, size="2"), spacing="0", align="end"),
            width="100%",
            align="center",
        ),
        padding="1rem",
        border_radius="18px",
        border="1px solid rgba(255,255,255,0.10)",
        background="rgba(255,255,255,0.04)",
        backdrop_filter="blur(10px)",
        width="100%",
    )


@rx.page(route="/recurring", title="Expense Tracker - Recurring")
def recurring_page() -> rx.Component:
    content = rx.vstack(
        rx.hstack(
            rx.text("Recurring templates", font_size="2rem", font_weight="900"),
            rx.spacer(),
            rx.button("Refresh", variant="surface", on_click=AppState.load_recurring_templates),
            width="100%",
            align="center",
        ),
        rx.text("These generate PENDING forecast expenses. Approve them in Expenses when they appear.", opacity=0.75),
        rx.divider(opacity=0.25),
        rx.cond(
            AppState.recurring_templates,
            rx.vstack(rx.foreach(AppState.recurring_templates, _template_card), spacing="2", width="100%"),
            rx.box(rx.text("No templates yet (or you don't have access).", opacity=0.75), padding="1rem"),
        ),
        spacing="3",
        width="100%",
    )

    return shell(rx.box(content, on_mount=AppState.load_recurring_templates))
