from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI

from .api.core.exceptions import register_exception_handlers
from .api.dependencies import get_current_user_id, get_db
from .api.v1.accounts import router as accounts_router
from .api.v1.expenses import router as expenses_router
from .api.v1.health import router as healthcheck_router
from .api.v1.memberships import router as memberships_router
from .api.v1.users import router as users_router
from .db.base import Base  # noqa: F401
from .services.currency_service import CurrencyService


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Syncing currency rates...")
    db = next(get_db())  # Get a manual session
    service = CurrencyService()
    await service.sync_rates(db)
    yield
    print("Shutting down...")


app = FastAPI(title="Expense Tracker API", lifespan=lifespan)

app.include_router(users_router, prefix="/api/v1")
app.include_router(accounts_router, prefix="/api/v1", dependencies=[Depends(get_current_user_id)])
app.include_router(expenses_router, prefix="/api/v1", dependencies=[Depends(get_current_user_id)])
app.include_router(memberships_router, prefix="/api/v1", dependencies=[Depends(get_current_user_id)])
app.include_router(healthcheck_router, prefix="/api/v1")

# Connect the handlers
register_exception_handlers(app=app)
