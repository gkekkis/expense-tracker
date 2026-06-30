from __future__ import annotations

import reflex as rx

from ..components.layout import shell
from ..state.app_state import AppState


def _status_badge(status: rx.Var) -> rx.Component:
    """Color-coded status badge."""
    # In Reflex 0.8.x, avoid python boolean ops on Vars; use rx.cond.
    return rx.cond(
        status == "Pending",
        rx.badge(status, variant="surface", color_scheme="amber"),
        rx.cond(
            status == "Completed",
            rx.badge(status, variant="surface", color_scheme="green"),
            rx.cond(
                status == "Cancelled",
                rx.badge(status, variant="surface", color_scheme="red"),
                rx.badge(status, variant="surface"),
            ),
        ),
    )


def _expense_row(e) -> rx.Component:
    desc = rx.cond(e.get("description"), e.get("description"), "-")
    status = rx.cond(e.get("status"), e.get("status"), "")
    amt = rx.cond(e.get("amount"), e.get("amount"), "0.00")
    cur = rx.cond(e.get("currency"), e.get("currency"), "")
    dt = rx.cond(e.get("expense_date"), e.get("expense_date"), "")

    cat_name = rx.cond(e.get("category_name"), e.get("category_name"), "")
    cat_emoji = rx.cond(e.get("category_emoji"), e.get("category_emoji"), "")

    approve_btn = rx.cond(
        status == "Pending",
        rx.button(
            "Approve",
            size="2",
            variant="soft",
            on_click=AppState.approve_expense(e.get("id")),
            disabled=AppState.is_viewer,
        ),
        rx.fragment(),
    )

    delete_btn = rx.button(
        "Delete",
        size="2",
        variant="surface",
        on_click=AppState.delete_expense(e.get("id")),
        disabled=AppState.is_viewer,
    )

    return rx.box(
        rx.hstack(
            rx.vstack(
                rx.hstack(
                    rx.text(desc, font_weight="700"), _status_badge(status), spacing="2", align="center", width="100%"
                ),
                rx.hstack(
                    rx.text(dt, opacity=0.7, size="2"),
                    rx.cond(
                        cat_name,
                        rx.hstack(
                            rx.text(cat_emoji), rx.text(cat_name, opacity=0.8, size="2"), spacing="1", align="center"
                        ),
                        rx.fragment(),
                    ),
                    spacing="3",
                    align="center",
                ),
                spacing="1",
                width="100%",
                align="start",
            ),
            rx.spacer(),
            rx.vstack(
                rx.text(f"{amt}", font_weight="800"), rx.text(cur, opacity=0.7, size="2"), spacing="0", align="end"
            ),
            rx.vstack(approve_btn, delete_btn, spacing="2", align="end"),
            spacing="3",
            width="100%",
            align="center",
        ),
        padding="0.9rem",
        border_radius="16px",
        border="1px solid rgba(255,255,255,0.08)",
        background="rgba(255,255,255,0.03)",
        backdrop_filter="blur(10px)",
    )


@rx.page(route="/expenses", title="Expense Tracker - Expenses")
def expenses_page() -> rx.Component:
    status_filters = rx.hstack(
        rx.checkbox("Pending", is_checked=AppState.f_status_pending, on_change=AppState.set_f_status_pending),
        rx.checkbox("Completed", is_checked=AppState.f_status_completed, on_change=AppState.set_f_status_completed),
        rx.checkbox("Cancelled", is_checked=AppState.f_status_cancelled, on_change=AppState.set_f_status_cancelled),
        spacing="4",
        align="center",
        flex_wrap="wrap",
    )

    hint = rx.cond(
        AppState.is_viewer,
        rx.callout(
            "You're a viewer in this account. You can browse, but you can't add/approve/delete expenses.",
            icon="info",
            variant="surface",
        ),
        rx.callout(
            "Tip: recurring templates create PENDING expenses. Use Approve on a pending row to mark it approved.",
            icon="info",
            variant="surface",
        ),
    )

    filters = rx.box(
        rx.vstack(
            rx.hstack(
                rx.input(
                    placeholder="Search description...",
                    value=AppState.f_search_query,
                    on_change=AppState.set_f_search_query,
                    width="100%",
                ),
                rx.input(
                    placeholder="Min", value=AppState.f_min_amount, on_change=AppState.set_f_min_amount, width="160px"
                ),
                rx.input(
                    placeholder="Max", value=AppState.f_max_amount, on_change=AppState.set_f_max_amount, width="160px"
                ),
                spacing="2",
                width="100%",
                flex_wrap="wrap",
            ),
            rx.hstack(
                rx.input(type_="date", value=AppState.f_start_date, on_change=AppState.set_f_start_date, width="200px"),
                rx.input(type_="date", value=AppState.f_end_date, on_change=AppState.set_f_end_date, width="200px"),
                rx.select(
                    items=AppState.category_select_items,
                    value=AppState.category_selected_item,
                    placeholder="All categories",
                    on_change=AppState.set_category_item,
                ),
                rx.button("Clear category", variant="surface", on_click=AppState.set_category_item("")),
                spacing="2",
                width="100%",
                flex_wrap="wrap",
            ),
            status_filters,
            rx.hstack(
                rx.select(
                    items=["EUR", "USD", "GBP"],
                    value=AppState.target_currency,
                    on_change=AppState.set_target_currency,
                    width="160px",
                ),
                rx.button("Search", on_click=AppState.search_expenses(True)),
                rx.spacer(),
                rx.text(AppState.expenses_total_amount_formatted, font_weight="800"),
                spacing="2",
                width="100%",
                align="center",
            ),
            spacing="2",
            width="100%",
        ),
        padding="1rem",
        border_radius="18px",
        border="1px solid rgba(255,255,255,0.10)",
        background="rgba(255,255,255,0.04)",
        backdrop_filter="blur(10px)",
        width="100%",
    )

    quick_add = rx.box(
        rx.vstack(
            rx.text("Quick add", font_weight="800"),
            rx.hstack(
                rx.input(
                    placeholder="Description",
                    value=AppState.exp_description,
                    on_change=AppState.set_exp_description,
                    width="100%",
                ),
                rx.input(
                    placeholder="Amount", value=AppState.exp_amount, on_change=AppState.set_exp_amount, width="180px"
                ),
                spacing="2",
                width="100%",
                flex_wrap="wrap",
            ),
            rx.hstack(
                rx.select(
                    items=AppState.category_select_items,
                    value=AppState.exp_category_selected_item,
                    on_change=AppState.set_exp_category_item,
                    placeholder="Pick a category",
                    width="340px",
                ),
                rx.input(type_="date", value=AppState.exp_date, on_change=AppState.set_exp_date, width="200px"),
                rx.select(
                    items=["Completed", "Pending", "Cancelled"],
                    value=AppState.exp_status,
                    on_change=AppState.set_exp_status,
                    width="180px",
                ),
                spacing="2",
                width="100%",
                flex_wrap="wrap",
            ),
            rx.hstack(
                rx.input(
                    placeholder="Personal factor (0..1) optional",
                    value=AppState.exp_personal_factor,
                    on_change=AppState.set_exp_personal_factor,
                    width="260px",
                ),
                rx.select(
                    items=["EUR", "USD", "GBP"],
                    value=AppState.exp_currency,
                    on_change=AppState.set_exp_currency,
                    width="160px",
                ),
                rx.spacer(),
                rx.button("Add expense", on_click=AppState.create_expense, disabled=AppState.is_viewer),
                spacing="2",
                width="100%",
                align="center",
            ),
            spacing="2",
            width="100%",
        ),
        padding="1rem",
        border_radius="18px",
        border="1px solid rgba(255,255,255,0.10)",
        background="rgba(255,255,255,0.04)",
        backdrop_filter="blur(10px)",
        width="100%",
    )

    listing = rx.vstack(
        rx.hstack(
            rx.text("Results", font_weight="900", font_size="1.4rem"),
            rx.spacer(),
            rx.text(rx.cond(AppState.expenses_total_count, f"{AppState.expenses_total_count} items", "")),
            width="100%",
            align="center",
        ),
        rx.cond(
            AppState.expenses,
            rx.vstack(rx.foreach(AppState.expenses, _expense_row), spacing="2", width="100%"),
            rx.box(rx.text("No expenses found. Try adjusting filters.", opacity=0.75), padding="1rem"),
        ),
        rx.hstack(
            rx.button("Prev", variant="surface", on_click=AppState.prev_page),
            rx.button("Next", variant="surface", on_click=AppState.next_page),
            spacing="2",
        ),
        spacing="3",
        width="100%",
    )

    content = rx.vstack(
        rx.hstack(
            rx.text("Expenses", font_size="2rem", font_weight="900"),
            rx.spacer(),
            rx.button("Refresh", variant="surface", on_click=AppState.search_expenses(True)),
            width="100%",
            align="center",
        ),
        rx.divider(opacity=0.25),
        hint,
        filters,
        quick_add,
        listing,
        spacing="4",
        width="100%",
    )

    return shell(rx.box(content, on_mount=[AppState.load_categories, AppState.search_expenses(True)]))
