import reflex as rx

from ..components.stats_cards import expenses_stats_cards
from ..state.account_detail_state import AccountDetailState
from ..state.auth_state import AuthState
from ..views.expenses_table import expenses_table
from ..views.navbar import navbar


def account_detail_page() -> rx.Component:
    return rx.vstack(
        navbar("Account", show_back=True),
        rx.vstack(
            rx.hstack(
                rx.vstack(
                    rx.heading(AccountDetailState.account_name, size="6"),
                    rx.text(
                        rx.cond(
                            AccountDetailState.account_status != "", "Status: " + AccountDetailState.account_status, ""
                        ),
                        color=rx.color("gray", 11),
                        size="2",
                    ),
                    spacing="1",
                    align_items="start",
                ),
                rx.spacer(),
                rx.button("Logout", variant="outline", on_click=AuthState.logout),
                width="100%",
                align="center",
            ),
            expenses_stats_cards(),  # ✅ cards back
            rx.box(expenses_table(), width="100%"),
            width="100%",
            spacing="6",
            padding_x=["1.5em", "1.5em", "3em"],
        ),
        width="100%",
        spacing="6",
    )
