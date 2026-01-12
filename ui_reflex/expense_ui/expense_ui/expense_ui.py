import reflex as rx

from .components.stats_cards import accounts_stats_cards
from .pages.account_detail import account_detail_page
from .pages.login import login_page
from .state.account_detail_state import AccountDetailState
from .state.accounts_state import AccountsState
from .state.auth_state import AuthState
from .views.accounts_table import accounts_table
from .views.navbar import navbar


def index_page() -> rx.Component:
    return rx.vstack(
        navbar("Expense Tracker", show_back=False),
        rx.vstack(
            rx.hstack(
                rx.vstack(
                    rx.heading(
                        rx.cond(AuthState.user_name != "", "Welcome, " + AuthState.user_name, "Welcome"), size="6"
                    ),
                    rx.text("Select an account to view expenses.", color=rx.color("gray", 11), size="2"),
                    spacing="1",
                    align_items="start",
                ),
                rx.spacer(),
                rx.button("Logout", variant="outline", on_click=AuthState.logout),
                width="100%",
                align="center",
                spacing="3",
            ),
            accounts_stats_cards(),
            rx.box(accounts_table(), width="100%"),
            width="100%",
            spacing="6",
            padding_x=["1.5em", "1.5em", "3em"],
        ),
        width="100%",
        spacing="6",
    )


app = rx.App(
    theme=rx.theme(
        appearance="inherit",
        has_background=True,
        # ... other theme settings
    )
)

app.add_page(login_page, route="/login", title="Login")

app.add_page(
    index_page,
    route="/",
    title="Expense Tracker",
    on_load=[AuthState.require_login, AuthState.load_user, AccountsState.load_accounts],
)

app.add_page(
    account_detail_page,
    route="/accounts/[account_id]",
    title="Account",
    on_load=[AuthState.require_login, AccountDetailState.load],  # ✅ will receive account_id
)
