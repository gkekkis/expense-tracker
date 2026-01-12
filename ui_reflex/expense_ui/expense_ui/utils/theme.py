import reflex as rx


def theme_toggle() -> rx.Component:
    return rx.button(
        # Change icon based on the current color mode
        rx.cond(rx.color_mode == "light", rx.icon(tag="moon", size=18), rx.icon(tag="sun", size=18)),
        on_click=rx.toggle_color_mode,
        variant="outline",
        padding="10px",
    )
