# Postman API Collection

This folder contains a Postman collection for manually testing the Expense Tracker API.

## Files

- `expense-tracker.postman_collection.json`: end-to-end request flows and assertions.
- `expense-tracker.local.postman_environment.json`: local variables for `http://127.0.0.1:8001`.

## Setup

Apply database migrations before running the collection:

```powershell
.venv\Scripts\python.exe -m alembic upgrade head
.venv\Scripts\python.exe -m alembic current
```

Expected Alembic version:

```text
f8a1c2b3d4e5 (head)
```

Make sure Alembic and Uvicorn are using the same database mode in the same terminal.

For the local development database configured by `TEST_DATABASE_URL`:

```powershell
$env:DEV = "True"
$env:TESTING = "False"
```

For the main local database configured by `DB_NAME` / `DATABASE_URL`:

```powershell
$env:DEV = "False"
$env:TESTING = "False"
$env:AUTH_SECRET_KEY = "local-postman-dev-secret-change-me"
```

Then start the backend:

```powershell
uvicorn app.main:app --reload --port 8001
```

Then import both JSON files into Postman and select the `Expense Tracker Local` environment.

## How To Run

Run the collection from top to bottom:

1. `00 Health`
2. `01 Users & Auth`
3. `02 Accounts & Categories`
4. `03 Memberships & RBAC`
5. `04 Expenses`
6. `05 Recurring Templates`
7. `06 Financial Profile & Summaries`

The first authenticated owner login stores `access_token`, which the collection uses by default.
Member and viewer requests use their own request-level bearer tokens.

## Resetting A Run

The collection generates unique test emails from `run_id` using the `expense-tracker.dev` domain.
To start a clean logical run, clear `run_id` in the selected Postman environment before running again.

If your database enforces unique emails, clearing `run_id` is enough because the next run will generate new email addresses.

## Auth Notes

The collection uses bearer tokens by default.

For local prototype testing only, the API can also accept `X-User-Id` when one of these environment flags is enabled:

- `DEV=True`
- `TESTING=True`
- `ALLOW_X_USER_ID_AUTH=True`

Prefer bearer tokens for manual QA because they exercise the real authentication path.

## Coverage

The collection covers:

- health check
- user creation and login
- account creation, listing, reading, and updating
- default category lookup
- membership creation and update
- viewer read-only checks
- expense create, list, read, search, update, approve, and delete
- member expense creation
- recurring template list, create, update, delete, and viewer denial
- financial profile read/update and viewer denial
- budget summary retrieval
