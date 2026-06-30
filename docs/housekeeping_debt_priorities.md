# Housekeeping And Technical Debt Priorities

Date: 2026-06-29

## Completed In This Pass

- Added updated product roadmap markdown and PDF.
- Added technical roadmap markdown and PDF.
- Added root `README.md`.
- Added `.env.example`.
- Replaced empty `Dockerfile` with a minimal backend runtime image.
- Updated root `requirements.txt` to include the actual backend/test/UI-adjacent dependencies.
- Updated `ui_reflex/requirements.txt` to include `httpx`.
- Cleaned `.gitignore` so project metadata and dependency files are no longer hidden.
- Fixed account creation so the current user becomes account OWNER.
- Fixed default category seeding to return category IDs.
- Fixed new-account onboarding to seed recurring templates with category UUIDs.
- Fixed recurring processing to catch up all due template occurrences.
- Fixed recurring processing to process all accounts when no account filter is supplied.
- Fixed expense search to honor `end_date`, `min_amount`, and `max_amount`.
- Fixed expense search total normalization to use all matching expenses rather than only the current page.
- Fixed budget summary filters to honor the filters exposed by the API.
- Fixed membership create/update to persist `default_contribution_share`.
- Added category name and emoji computed fields to expense responses for the current UI.
- Removed an unpersisted financial-profile response field.
- Fixed test environment bootstrapping so the scheduler does not start during tests.
- Added regression coverage for account creation ownership/category seeding.
- Added Alembic migration for financial profiles, membership shares, responsibility fields, and recurring-template ownership/currency fields.
- Ignored Reflex generated state caches from the root `.gitignore`.
- Synced the project virtual environment with `requirements.txt`.
- Reworked Ruff settings into a practical baseline and moved deprecated config keys.
- Simplified stale pre-commit configuration around core hygiene checks, gitleaks, and Ruff.
- Ran Ruff format/check successfully.
- Cleaned several encoding artifacts in the active Reflex UI pages.
- Documented a disposable-database Alembic migration smoke test.
- Added signed bearer-token authentication baseline with password hashing.
- Restricted `X-User-Id` authentication to local prototype and test flows.
- Added account-scoped read authorization for accounts, expenses, memberships, categories, financial profiles, and budget summaries.
- Added API regression tests proving non-members cannot read account-owned resources.
- Restricted global user discovery to local prototype flows and added authenticated exact-email user search.
- Added environment-driven CORS configuration for frontend/API browser access.

## Priority 0: Clean Baseline Before Product Work

- Decide and commit the active UI path: keep `ui_reflex/ui_reflex`, remove old `ui_reflex/expense_ui`.
- Decide whether to reset local/dev databases or backfill historical expenses before relying on migrations with existing data.
- Add `.env.example` values to any setup docs that need them.
- Run `pre-commit run --all-files` after deciding whether to include untracked/generated docs in the first cleanup commit.
- Confirm a fresh clone can run backend tests from README instructions.

## Priority 1: Security And Data Isolation

- Remove `X-User-Id` fallback before any non-local deployment.
- Enforce VIEWER read-only behavior in backend services.
- Add audit logging for account, membership, profile, and expense changes.

## Priority 2: Database And Migration Health

- Verify migrations against both a fresh database and any existing local/dev databases.
- Decide whether to reset local/dev data or backfill category IDs safely before relying on historical migrations with existing expenses.
- Review enum usage and native/non-native enum consistency.
- Remove destructive `init_db` flows from normal development paths.

## Priority 3: API Correctness

- Add tests for each role and each protected endpoint.
- Validate category ownership on expense creation, not only update/search.
- Decide whether total amount should include cancelled/pending expenses by default and document behavior.
- Add stable pagination metadata and next/previous semantics.
- Add typed error responses for validation and external service failures.

## Priority 4: Frontend Cleanup

- Replace temporary Overview with a Today/Financial GPS page.
- Reduce emoji-heavy styling and move toward a calmer product UI.
- Show category name/emoji from backend response consistently.
- Add real loading/error/empty states.
- Add membership share editing UI.
- Add recurring-template create/update UI.
- Decide whether Reflex remains the long-term frontend before building complex workflows.

## Priority 5: Product-MVP Foundations

- Add CSV import before bank aggregation.
- Add safe-to-spend v0.
- Add cash-flow timeline.
- Add action inbox data model.
- Add weekly summary generation.
- Add recommendation feedback tracking.

## Priority 6: AI/Agent Foundations

- Create labeled transaction categorization fixtures.
- Build rules-first insights before LLM calls.
- Add LLM categorization only with confidence thresholds and evaluation.
- Add action ledger before agent execution.
- Add approval policies before any external action.
