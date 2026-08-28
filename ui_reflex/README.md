# Expense Tracker UI (Reflex)

This is a Reflex frontend for your FastAPI Expense Tracker.

## Prereqs
- Python 3.10+
- Backend running (your FastAPI app)

## Install
```bash
pip install reflex httpx
```

## Configure
Set the backend base URL (defaults to `http://127.0.0.1:8001`).

```bash
export API_BASE_URL=http://127.0.0.1:8001
```

Allow the Reflex origin in the backend `.env`:

```bash
CORS_ALLOW_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

## Run
From the repo root:
```bash
reflex init
# When asked, point to the app module if needed
reflex run
```

If your Reflex version expects a config file, create `rxconfig.py`:

```python
import reflex as rx

config = rx.Config(
    app_name="expense_ui",
)
```

## Pages
- `/` Sign in / user switch (uses local-prototype `GET /api/v1/users/`)
- `/accounts` list & create accounts (uses `GET /api/v1/users/me/accounts` + `POST /api/v1/accounts/`)
- `/overview` account overview
- `/expenses` search + quick add + approve pending
- `/recurring` list recurring templates
- `/members` manage memberships (owner-only)
- `/budget` budget status + financial profile
- `/settings`

## Notes
- Auth is still prototype-oriented in this UI. It uses `X-User-Id` and the local-only global user picker, so run the
  backend with `DEV=True`, `TESTING=True`, or `ALLOW_X_USER_ID_AUTH=True` when using this Reflex app.
- The backend must include the Reflex browser origin in `CORS_ALLOW_ORIGINS`.
- VIEWER is treated as read-only in the UI.
