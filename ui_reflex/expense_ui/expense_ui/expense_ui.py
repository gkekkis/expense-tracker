import reflex as rx

from .pages.login import login_page
from .state.accounts_state import AccountsState
from .state.auth_state import AuthState


def index_page() -> rx.Component:
    return rx.vstack(
        rx.hstack(
            rx.heading("Expense Tracker", size="6"),
            rx.spacer(),
            rx.button("Logout", variant="outline", on_click=AuthState.logout),
            width="100%",
        ),
        rx.cond(
            AccountsState.loading,
            rx.text("Loading accounts..."),
            rx.cond(
                AccountsState.error != "",
                rx.box(
                    rx.text(AccountsState.error, color="red"),
                    rx.cond(
                        AccountsState.error_code != "",
                        rx.text(f"({AccountsState.error_code})", color="gray", size="2"),
                        rx.fragment(),
                    ),
                    padding="12px",
                    border="1px solid #333",
                    border_radius="12px",
                    width="100%",
                ),
                rx.vstack(
                    rx.heading("Your accounts", size="4"),
                    rx.cond(
                        AccountsState.accounts.length() == 0,
                        rx.text("No accounts found."),
                        rx.vstack(
                            rx.foreach(
                                AccountsState.accounts,
                                lambda a: rx.box(
                                    rx.text(a["name"], weight="bold"),
                                    rx.text(a["status"], color="gray", size="2"),
                                    rx.text(a["id"], color="gray", size="2"),
                                    rx.text(f'Created at: {a["created_at"]}', color="gray", size="2"),
                                    rx.text(f'Updated at: {a["updated_at"]}', color="gray", size="2"),
                                    padding="12px",
                                    border="1px solid #333",
                                    border_radius="12px",
                                    width="100%",
                                ),
                            ),
                            spacing="2",
                            width="100%",
                        ),
                    ),
                    spacing="3",
                    width="100%",
                ),
            ),
        ),
        padding="24px",
        max_width="900px",
        margin="0 auto",
        width="100%",
        spacing="4",
    )


app = rx.App(theme=rx.theme(appearance="dark", has_background=True, radius="large", accent_color="grass"))

# Public
app.add_page(login_page, route="/login", title="Login")

# Protected + load accounts on entry
app.add_page(
    index_page, route="/", title="Expense Tracker", on_load=[AuthState.require_login, AccountsState.load_accounts]
)
