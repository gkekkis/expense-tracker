import os

# FastAPI base URL (your real backend)
FASTAPI_BASE_URL = os.getenv("FASTAPI_BASE_URL", "http://localhost:8000")

# API paths (no hardcoding in state/pages)
GET_ACCOUNTS_PATH = os.getenv("GET_ACCOUNTS_PATH", "/api/v1/accounts")
