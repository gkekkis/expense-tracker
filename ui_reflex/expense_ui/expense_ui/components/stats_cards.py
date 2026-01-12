import reflex as rx

from ..state.account_detail_state import AccountDetailState
from ..state.accounts_state import AccountsState


def _stat_card(icon: str, title: str, value):
    return rx.card(
        rx.hstack(
            rx.badge(rx.icon(icon, size=20), radius="full", color_scheme="grass", variant="soft"),
            rx.vstack(
                rx.text(title, color=rx.color("gray", 11), size="2"),
                rx.heading(value, size="6"),
                spacing="1",
                align_items="start",
            ),
            spacing="3",
            align="center",
        ),
        width="100%",
    )


def accounts_stats_cards() -> rx.Component:
    return rx.grid(
        _stat_card("layers", "Total Accounts", AccountsState.total_accounts),
        _stat_card("badge-check", "Active Accounts", AccountsState.active_accounts),
        _stat_card("ban", "Inactive Accounts", AccountsState.inactive_accounts),
        columns=rx.breakpoints(initial="1", sm="2", lg="3"),
        spacing="4",
        width="100%",
        margin_top="1em",
    )


def expenses_stats_cards() -> rx.Component:
    return rx.grid(
        _stat_card("receipt_euro", "Total Expenses", AccountDetailState.total_expenses),
        _stat_card("wallet", "Total Amount", AccountDetailState.total_amount),
        _stat_card("tag", "Top Category", AccountDetailState.top_category),
        columns=rx.breakpoints(initial="1", sm="2", lg="3"),
        spacing="4",
        width="100%",
        margin_top="1em",
    )
