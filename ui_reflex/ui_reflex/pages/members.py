from __future__ import annotations

import reflex as rx

from ..components.layout import shell
from ..state.app_state import AppState


def _member_row(m) -> rx.Component:
    user_id = m.get("user_id")
    role = rx.cond(m.get("role"), m.get("role"), "")
    share = rx.cond(m.get("default_contribution_share"), m.get("default_contribution_share"), "1.00")

    # Prefer enriched fields if backend provides them (common pattern in your app).
    display_name = rx.cond(m.get("user_name"), m.get("user_name"), user_id)
    email = rx.cond(m.get("user_email"), m.get("user_email"), "")

    return rx.box(
        rx.hstack(
            rx.vstack(
                rx.hstack(
                    rx.text(display_name, font_weight="800"),
                    rx.cond(email, rx.text(email, opacity=0.7, size="2"), rx.fragment()),
                    spacing="2",
                    align="center",
                ),
                rx.hstack(
                    rx.badge(role, variant="surface"),
                    rx.text(f"Share: {share}", opacity=0.75, size="2"),
                    spacing="2",
                    align="center",
                ),
                spacing="1",
                align="start",
            ),
            rx.spacer(),
            rx.cond(
                AppState.is_owner,
                rx.hstack(
                    rx.select(
                        items=["OWNER", "MEMBER", "VIEWER"],
                        value=role,
                        on_change=lambda v: AppState.update_membership(m.get("id"), role=v),
                        width="180px",
                    ),
                    rx.button("Remove", variant="surface", on_click=AppState.delete_membership(m.get("id"))),
                    spacing="2",
                    align="center",
                ),
                rx.fragment(),
            ),
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


@rx.page(route="/members", title="Expense Tracker · Members")
def members_page() -> rx.Component:
    header = rx.hstack(
        rx.text("Members", font_size="2rem", font_weight="900"),
        rx.spacer(),
        rx.button("Refresh", variant="surface", on_click=AppState.load_memberships),
        width="100%",
        align="center",
    )

    add_member_box = rx.box(
        rx.vstack(
            rx.hstack(
                rx.text("Add member", font_weight="900"),
                rx.spacer(),
                rx.badge(rx.cond(AppState.is_owner, "Owner controls enabled", "Read-only"), variant="surface"),
                width="100%",
                align="center",
            ),
            rx.text(
                "Pick an existing user and assign a role. Server enforces rules (e.g., first owner / last owner).",
                opacity=0.75,
            ),
            rx.hstack(
                rx.select(
                    items=AppState.user_select_items,
                    value=AppState.user_selected_item,
                    on_change=AppState.set_add_member_user_item,
                    placeholder="Select a user…",
                    width="420px",
                    is_disabled=~AppState.is_owner,
                ),
                rx.select(
                    items=["MEMBER", "VIEWER", "OWNER"],
                    value=AppState.add_member_role,
                    on_change=AppState.set_add_member_role,
                    width="200px",
                    is_disabled=~AppState.is_owner,
                ),
                rx.button("Add", on_click=AppState.add_member, disabled=~AppState.is_owner),
                spacing="2",
                width="100%",
                flex_wrap="wrap",
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
            rx.text("Current members", font_weight="900", font_size="1.2rem"),
            rx.spacer(),
            rx.cond(AppState.memberships, rx.text("", opacity=0.7), rx.text("")),
            width="100%",
            align="center",
        ),
        rx.cond(
            AppState.memberships,
            rx.vstack(rx.foreach(AppState.memberships, _member_row), spacing="2", width="100%"),
            rx.box(rx.text("No memberships loaded yet.", opacity=0.75), padding="1rem"),
        ),
        spacing="3",
        width="100%",
    )

    content = rx.vstack(header, rx.divider(opacity=0.25), add_member_box, listing, spacing="4", width="100%")

    return shell(rx.box(content, on_mount=[AppState.load_users, AppState.load_memberships]))
