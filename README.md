# Expense Tracker

Financial management MVP built with FastAPI, SQLAlchemy/Postgres, Alembic, and a Reflex prototype UI.

The current product direction is documented in:

- `docs/updated_product_roadmap.md`
- `docs/updated_product_roadmap.pdf`
- `docs/technical_roadmap.md`
- `docs/technical_roadmap.pdf`

## Current Status

This repository is being cleaned up into a stable build base. The backend already includes users, accounts, memberships, expenses, categories, recurring templates, currency normalization, financial profiles, and budget summaries. The UI is currently a Reflex prototype and should be treated as temporary product scaffolding.

## Setup

Create a virtual environment and install dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Copy environment settings:

```powershell
Copy-Item .env.example .env
```

Update `.env` with local Postgres database URLs and any API keys.

## Backend

Run migrations:

```powershell
alembic upgrade head
```

Migration smoke test against a disposable database:

```powershell
@'
from sqlalchemy import create_engine, text

admin_url = "postgresql+psycopg2://postgres:postgres123@localhost:5432/postgres"
db_name = "my_expense_report_migration_smoke"

engine = create_engine(admin_url, isolation_level="AUTOCOMMIT")
with engine.connect() as conn:
    conn.execute(text(f"DROP DATABASE IF EXISTS {db_name} WITH (FORCE)"))
    conn.execute(text(f"CREATE DATABASE {db_name}"))

print(f"Created clean DB: {db_name}")
'@ | .venv\Scripts\python.exe -

$env:DEV = "False"
$env:TESTING = "False"
$env:DATABASE_URL = "postgresql+psycopg2://postgres:postgres123@localhost:5432/my_expense_report_migration_smoke"

.venv\Scripts\python.exe -m alembic upgrade head
.venv\Scripts\python.exe -m alembic current
```

Expected Alembic version:

```text
f8a1c2b3d4e5 (head)
```

Start the API:

```powershell
uvicorn app.main:app --reload --port 8001
```

Configure browser origins that may call the API:

```env
CORS_ALLOW_ORIGINS=http://localhost:3000,http://127.0.0.1:3000,http://localhost:8000,http://127.0.0.1:8000
```

Use only your deployed frontend origin in production.

Health check:

```text
GET http://127.0.0.1:8001/api/v1/health/
```

Login with email/password:

```text
POST http://127.0.0.1:8001/api/v1/auth/login
```

Use the returned token on protected API calls:

```text
Authorization: Bearer <access_token>
```

For local prototype work only, `X-User-Id` and the global `GET /api/v1/users/` user picker can be enabled
with `DEV=True`, `TESTING=True`, or `ALLOW_X_USER_ID_AUTH=True`.

For normal authenticated flows, use `GET /api/v1/auth/me` for the current user and `GET /api/v1/users/search?email=...`
for exact email lookup before adding a member.

## Frontend

The active Reflex app lives in `ui_reflex/`.

```powershell
cd ui_reflex
reflex run
```

Set `API_BASE_URL` if the backend is not running on `http://127.0.0.1:8001`.

## Tests

Tests require a Postgres database configured by `PYTEST_DATABASE_URL`.

```powershell
$env:TESTING = "true"
pytest
```

The test setup drops and recreates the `public` schema in the configured test database.

## Notes

Authentication now supports signed bearer tokens. The `X-User-Id` fallback and global user listing are only for local
prototype and test flows.
