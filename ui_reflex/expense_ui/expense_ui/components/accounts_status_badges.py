import reflex as rx


def _badge(icon: str, text: str, color_scheme: str):
    return rx.badge(rx.icon(icon, size=16), text, color_scheme=color_scheme, radius="full", variant="soft", size="3")


def accounts_status_badge(status: str):
    badge_mapping = {"Active": ("badge_check", "Active", "green"), "Inactive": ("badge", "Inactive", "red")}
    return _badge(*badge_mapping.get(status, ("badge_check", "Active", "yellow")))
