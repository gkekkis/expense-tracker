# Expense Tracker

Financial decision platform built with FastAPI, SQLAlchemy/Postgres, and Alembic. The frontend is being rebuilt from a new design.

The current product direction is documented in the Markdown roadmaps:

- `docs/updated_product_roadmap.md`
- `docs/technical_roadmap.md`

The PDF files under `docs/` are dated 2026-06-29 snapshots and are retained only as historical exports. They are not current sources of truth.

## Current Status

The backend includes users, accounts, memberships, expenses, categories, recurring templates, currency normalization, financial profiles, budget summaries, signed bearer authentication, account-scoped authorization, and audit logging. There is no frontend in the repository while it is rebuilt; the previous Reflex prototype remains in the git history.

The product is planned as one platform with Personal and Professional editions. Personal and shared-household workflows receive slight chronological priority so the founder can test them directly; Professional remains the intended commercial wedge. The current milestone is a secure private shared-platform draft deployed on Azure; see `docs/updated_product_roadmap.md` for scope and `docs/technical_roadmap.md` for the implementation direction.

## Setup

Install the locked project dependencies with `uv`:

```powershell
uv sync --locked
.\.venv\Scripts\Activate.ps1
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
# Alembic reads DATABASE_URL when DEV and TESTING are both False.
$env:DATABASE_URL = "postgresql+psycopg2://postgres:postgres123@localhost:5432/my_expense_report_migration_smoke"

.venv\Scripts\python.exe -m alembic upgrade head
.venv\Scripts\python.exe -m alembic current
```

The running FastAPI application uses `DB_USER`, `DB_PASSWORD`, `DB_HOST`,
`DB_PORT`, and `DB_NAME` in this mode. Alembic currently uses `DATABASE_URL`,
so set that variable explicitly when running migrations outside the local
default setup.

Expected Alembic version:

```text
9b1d4f6e7a8c (head)
```

Start the API:

```powershell
uvicorn app.main:app --reload --port 8001
```

## Container Image

Build the FastAPI runtime image from the locked dependencies:

```powershell
docker build --tag expense-tracker-api:local .
```

The container needs the normal production database and authentication environment variables at runtime. When it connects to a local PostgreSQL instance through Docker Desktop, set `DB_HOST=host.docker.internal` rather than `localhost`.

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

The frontend is being rebuilt from a new design as a React and TypeScript single-page application; see "Frontend Architecture" in `docs/technical_roadmap.md`. The previous Reflex prototype was removed from the working tree and can be inspected in the git history, for example `git show 6193fe2:ui_reflex/ui_reflex/state/app_state.py`.

## Tests

Tests require a Postgres database configured by `PYTEST_DATABASE_URL`. The test setup drops and recreates the `public` schema in that database, so point it only at a disposable test database.

```powershell
$env:TESTING = "true"
uv run pytest tests/test_auth_baseline.py               # narrow run, no coverage
uv run pytest --cov=app --cov-report=term-missing       # full run, enforces the coverage threshold
```

Coverage is measured with branch coverage. The minimum is `fail_under` under `[tool.coverage.report]` in `pyproject.toml`, compared at two decimals (`precision = 2`, so 75.99% fails a 76% minimum), and a full local run and CI fail the same way. Every run with `--cov` enforces it, so run narrow test selections without `--cov`.

## Quality Checks

Install the Git hook once:

```powershell
uv run pre-commit install
```

The hooks in `.pre-commit-config.yaml` run on every commit: file hygiene checks, gitleaks on the staged changes, and Ruff lint and format. Ruff runs from the locked environment (`uv run --locked ruff`), so `pyproject.toml` and `uv.lock` hold its only version pin. Upgrade Ruff with `uv lock --upgrade-package ruff` after changing its pin; upgrade the other hook repositories with `uv run pre-commit autoupdate --freeze`, which keeps them pinned to commit SHAs. To run every hook, including the gitleaks scan of the git history that CI runs:

```powershell
uv run pre-commit run --all-files --hook-stage manual
```

CI (`.github/workflows/ci.yml`) runs on every pull request into `dev` and `main` with three jobs: `quality` (all pre-commit hooks, including the history scan), `tests` (pytest with coverage against PostgreSQL 17), and `migrations` (`alembic upgrade head` on a fresh database). The branch rulesets require these job names; renaming a job requires updating the rulesets.

### If The Secret Scan Finds Something

A pushed commit is public, and GitHub keeps it reachable even after a branch is rewritten. gitleaks reports a secret on the commit that added it and, while the secret is still part of a pull request's change, also on the merge commit that CI tests (`refs/pull/N/merge`, message `Merge <sha> into <sha>`). GitHub recreates that merge commit whenever the pull request or its base branch changes, so a finding on it cannot be suppressed; it disappears only when the secret leaves the files.

1. Revoke and rotate the secret first. Then check the provider's access logs (Azure, the database, the API provider) for use since the push; if the secret could reach user or financial data, treat it as a possible data breach.
2. Remove the secret from the files, in every case.
3. Clear the old commits, either way:
   - on an unmerged branch, rewrite the branch to drop the commit (the force push needs the repository owner's approval); or
   - otherwise, including on `dev` or `main`, add every commit-scoped fingerprint gitleaks reports on a real commit (`<commit>:<file>:<rule>:<line>`), including merge commits that carry the secret, to `.gitleaksignore` in the same pull request that removes it, with a `#` comment recording the rotation. Never use the global `<file>:<rule>:<line>` form.
4. For a false positive, add an inline `gitleaks:allow` comment on that line and justify it in the pull request. If the line is already in a pushed commit, that commit still reports it; clear it as in step 3.

`.gitleaksignore` entries and inline `gitleaks:allow` comments change the gate itself, so they get a security review. A `.gitleaks.toml`, if one is ever added, must set `[extend] useDefault = true`; without it, it replaces the default rules.

## Notes

Authentication now supports signed bearer tokens. The `X-User-Id` fallback and global user listing are only for local
prototype and test flows.
