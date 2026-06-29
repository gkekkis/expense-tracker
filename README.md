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

Start the API:

```powershell
uvicorn app.main:app --reload --port 8001
```

Health check:

```text
GET http://127.0.0.1:8001/api/v1/health/
```

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

Authentication is still prototype-level and uses `X-User-Id`. Do not use this as-is for real users.
