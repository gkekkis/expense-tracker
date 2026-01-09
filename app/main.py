from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.core.exceptions import register_exception_handlers
from .api.dependencies import get_current_user_id
from .api.v1.accounts import router as accounts_router
from .api.v1.expenses import router as expenses_router
from .api.v1.health import router as health_router
from .api.v1.memberships import router as memberships_router
from .api.v1.users import router as users_router

app = FastAPI(title="Expense Tracker API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users_router, prefix="/api/v1")
app.include_router(accounts_router, prefix="/api/v1", dependencies=[Depends(get_current_user_id)])
app.include_router(memberships_router, prefix="/api/v1", dependencies=[Depends(get_current_user_id)])
app.include_router(expenses_router, prefix="/api/v1", dependencies=[Depends(get_current_user_id)])
app.include_router(health_router, prefix="/api/v1")

# Connect the handlers
register_exception_handlers(app=app)
