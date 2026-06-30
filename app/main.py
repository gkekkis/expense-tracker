import os
from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv
from fastapi import Depends, FastAPI

from .api.core.exceptions import register_exception_handlers
from .api.dependencies import get_current_user_id, get_db
from .api.v1.accounts import router as accounts_router
from .api.v1.auth import router as auth_router
from .api.v1.expenses import router as expenses_router  # noqa: F401
from .api.v1.financial_profiles import router as financial_profiles_router  # noqa: F401
from .api.v1.health import router as healthcheck_router  # noqa: F401
from .api.v1.memberships import router as memberships_router  # noqa: F401
from .api.v1.recurring_templates import router as recurring_templates_router  # noqa: F401
from .api.v1.summaries import router as summaries_router  # noqa: F401
from .api.v1.users import router as users_router
from .core.scheduler import start_scheduler, stop_scheduler
from .db.base import Base  # noqa: F401
from .services.currency_service import CurrencyService

# 1. Setup path and load .env
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

is_test = os.getenv("TESTING", "False").lower() == "true"


@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- STARTUP ---
    if not is_test:
        print("Syncing currency rates...")
        db = next(get_db())
        service = CurrencyService()
        await service.sync_rates(db)
        print("Initializing background scheduler...")
        start_scheduler()

    yield

    # --- SHUTDOWN ---
    if not is_test:
        print("Shutting down scheduler...")
        stop_scheduler()
        print("Shutting down API...")


app = FastAPI(title="Expense Tracker API", lifespan=lifespan)

app.include_router(auth_router, prefix="/api/v1")
app.include_router(users_router, prefix="/api/v1")
app.include_router(accounts_router, prefix="/api/v1", dependencies=[Depends(get_current_user_id)])
app.include_router(expenses_router, prefix="/api/v1", dependencies=[Depends(get_current_user_id)])
app.include_router(memberships_router, prefix="/api/v1", dependencies=[Depends(get_current_user_id)])
app.include_router(financial_profiles_router, prefix="/api/v1", dependencies=[Depends(get_current_user_id)])
app.include_router(recurring_templates_router, prefix="/api/v1", dependencies=[Depends(get_current_user_id)])
app.include_router(summaries_router, prefix="/api/v1", dependencies=[Depends(get_current_user_id)])
app.include_router(healthcheck_router, prefix="/api/v1")

# Connect the handlers
register_exception_handlers(app=app)
