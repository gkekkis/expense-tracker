import os

# FastAPI base URL (your real backend)
FASTAPI_BASE_URL = os.getenv("FASTAPI_BASE_URL", "http://localhost:8000")

# API paths (no hardcoding in state/pages)
GET_ACCOUNTS_PATH = os.getenv("GET_ACCOUNTS_PATH", "/api/v1/accounts")
GET_MY_ACCOUNTS_PATH = "/api/v1/users/me/accounts"


GET_USERS_PATH = os.getenv("GET_USERS_PATH", "/api/v1/users")
GET_USER_BY_ID_PATH = "/api/v1/users"
GET_ACCOUNT_BY_ID_PATH = "/api/v1/accounts/{account_id}"
GET_ACCOUNT_EXPENSES_PATH = "/api/v1/accounts/{account_id}/expenses"
