import reflex as rx

from ..state.account_detail_state import AccountDetailState


def _header_cell(text: str, icon: str) -> rx.Component:
    return rx.table.column_header_cell(rx.hstack(rx.icon(icon, size=18), rx.text(text), align="center", spacing="2"))


def show_expense(e) -> rx.Component:
    return rx.table.row(
        rx.table.cell(rx.text(e.description, weight="medium")),
        rx.table.cell(rx.badge(e.category, variant="surface", radius="full")),
        rx.table.cell(rx.text(f"€{e.amount}")),
        rx.table.cell(rx.text(e.expense_date, color="gray", size="2")),
        style={"_hover": {"bg": rx.color("gray", 2)}},
        align="center",
    )


def expenses_table() -> rx.Component:
    return rx.cond(
        AccountDetailState.loading,
        rx.text("Loading expenses..."),
        rx.cond(
            AccountDetailState.error != "",
            rx.callout(AccountDetailState.error, icon="triangle-alert", color_scheme="red", variant="surface"),
            rx.cond(
                AccountDetailState.expenses.length() == 0,
                rx.text("No expenses for this account yet."),
                rx.table.root(
                    rx.table.header(
                        rx.table.row(
                            _header_cell("Description", "file-text"),
                            _header_cell("Category", "tag"),
                            _header_cell("Amount", "euro"),
                            _header_cell("Date", "calendar"),
                        )
                    ),
                    rx.table.body(rx.foreach(AccountDetailState.expenses, show_expense)),
                    variant="surface",
                    size="3",
                    width="100%",
                ),
            ),
        ),
    )
