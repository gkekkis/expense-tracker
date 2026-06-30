from __future__ import annotations

import reflex as rx

from .pages.accounts import accounts_page
from .pages.budget import budget_page
from .pages.expenses import expenses_page
from .pages.login import login_page
from .pages.members import members_page
from .pages.overview import overview_page
from .pages.recurring import recurring_page
from .pages.settings import settings_page

app = rx.App(theme=rx.theme(appearance="dark", radius="large", accent_color="violet"))

app.add_page(login_page)
app.add_page(accounts_page)
app.add_page(overview_page)
app.add_page(expenses_page)
app.add_page(recurring_page)
app.add_page(members_page)
app.add_page(budget_page)
app.add_page(settings_page)
