from fastapi import FastAPI

from .api.core.exceptions import register_exception_handlers
from .api.v1.accounts import router as accounts_router
from .api.v1.expenses import router as expenses_router
from .api.v1.memberships import router as memberships_router
from .api.v1.users import router as users_router

app = FastAPI(title="Expense Tracker API")

app.include_router(users_router, prefix="/api/v1")
app.include_router(accounts_router, prefix="/api/v1")
app.include_router(memberships_router, prefix="/api/v1")
app.include_router(expenses_router, prefix="/api/v1")

# Connect the handlers
register_exception_handlers(app=app)
