# expense_ui/views/accounts_table.py
import reflex as rx

from ..models import Account
from ..state.accounts_state import AccountsState


def _header_cell(text: str, icon: str) -> rx.Component:
    return rx.table.column_header_cell(rx.hstack(rx.icon(icon, size=18), rx.text(text), align="center", spacing="2"))


def show_account(a: Account) -> rx.Component:
    return rx.table.row(
        rx.table.cell(rx.text(a.name, weight="bold")),
        rx.table.cell(rx.text(a.status, color="gray", size="2")),
        rx.table.cell(rx.text(a.updated_at[:10], color="gray", size="2")),
        on_click=rx.redirect("/accounts/" + a.id),
        style={"_hover": {"bg": rx.color("gray", 3)}},
        cursor="pointer",
        align="center",
    )


def accounts_table() -> rx.Component:
    return rx.cond(
        AccountsState.loading,
        rx.text("Loading accounts."),
        rx.cond(
            AccountsState.error != "",
            rx.callout(AccountsState.error, icon="triangle-alert", color_scheme="red", variant="surface"),
            rx.table.root(
                rx.table.header(
                    rx.table.row(
                        _header_cell("Name", "user"),
                        _header_cell("Status", "badge-check"),
                        _header_cell("Updated", "calendar"),
                    )
                ),
                rx.table.body(rx.foreach(AccountsState.accounts, show_account)),
                variant="surface",
                size="3",
                width="100%",
            ),
        ),
    )
