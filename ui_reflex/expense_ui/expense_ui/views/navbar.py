import reflex as rx

from ..utils.theme import theme_toggle


def navbar(title: str = "Expense Tracker", show_back: bool = False) -> rx.Component:
    return rx.hstack(
        rx.hstack(
            rx.cond(show_back, rx.button("← Back", variant="ghost", on_click=rx.redirect("/")), rx.fragment()),
            rx.badge(
                rx.icon("layout-grid", size=18),
                rx.text(title, weight="bold"),
                radius="large",
                variant="surface",
                size="3",
            ),
            spacing="3",
            align="center",
        ),
        rx.spacer(),
        rx.hstack(
            rx.text("Built with", color=rx.color("gray", 11), size="2"),
            rx.text("REFLEX", weight="bold", size="2"),
            spacing="2",
            align="center",
        ),
        rx.hstack(
            rx.heading("Expense Tracker", size="7"),
            rx.spacer(),
            theme_toggle(),
            width="100%",
            align="center",
            padding="2em",
        ),
        width="100%",
        padding_y="1.25em",
    )
