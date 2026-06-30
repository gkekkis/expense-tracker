from __future__ import annotations

import reflex as rx

from ..components.layout import shell
from ..state.app_state import AppState


def _user_button(u) -> rx.Component:
    """
    Render a user selector row.
    Avoid Python string concatenation with Vars; compose UI with rx.text instead.
    """
    name = rx.cond(u["name"], u["name"], "Unknown")
    email = rx.cond(u["email"], u["email"], "")

    return rx.button(
        rx.hstack(
            rx.text(name, font_weight="600"),
            rx.cond(email, rx.text(" · ", opacity=0.6), rx.fragment()),
            rx.cond(email, rx.text(email, opacity=0.8), rx.fragment()),
            spacing="1",
            width="100%",
            justify="start",
        ),
        variant="surface",
        width="100%",
        on_click=AppState.pick_user(u["id"], name),
    )


@rx.page(route="/", title="Expense Tracker · Sign in")
def login_page() -> rx.Component:
    content = rx.center(
        rx.box(
            rx.vstack(
                rx.hstack(
                    rx.text("Welcome back", font_size="2rem", font_weight="800"),
                    rx.text("👋", font_size="2rem"),
                    align="center",
                ),
                rx.text("Pick a user (header-based auth) or create a new one.", opacity=0.75),
                rx.divider(opacity=0.25),
                rx.button("Load users", on_click=AppState.load_users, width="100%"),
                rx.cond(
                    AppState.users,
                    rx.vstack(
                        rx.text("Users", font_weight="700"),
                        rx.vstack(rx.foreach(AppState.users, _user_button), spacing="2", width="100%"),
                        spacing="2",
                        width="100%",
                    ),
                    rx.box(),
                ),
                rx.divider(opacity=0.25),
                rx.text("Create user", font_weight="700"),
                rx.input(placeholder="Name", value=AppState.new_user_name, on_change=AppState.set_new_user_name),
                rx.input(placeholder="Email", value=AppState.new_user_email, on_change=AppState.set_new_user_email),
                rx.button("Create & sign in", on_click=AppState.create_user, width="100%"),
                spacing="3",
                width="420px",
            ),
            padding="1.4rem",
            border_radius="18px",
            border="1px solid rgba(255,255,255,0.10)",
            background="rgba(255,255,255,0.04)",
            backdrop_filter="blur(10px)",
        ),
        min_height="100vh",
    )
    return shell(content)
