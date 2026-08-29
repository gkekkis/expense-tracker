# Expense Tracker Agent Guide

## Purpose

Expense Tracker is evolving from a manual expense tracker into a financial decision platform focused initially on freelancers and solo professionals.

The backend is currently the most mature part of the product.

The existing Reflex frontend is prototype scaffolding only and may be heavily refactored or replaced entirely.

## Sources Of Truth

Before making product or architecture decisions, consult the relevant documentation:

* `README.md` — current setup and development commands.
* `docs/updated_product_roadmap.md` — product direction and priorities.
* `docs/technical_roadmap.md` — technical direction.

Do not duplicate those documents inside this file.

## Current Architecture

Backend:

* FastAPI
* SQLAlchemy
* PostgreSQL
* Alembic

Frontend:

* Current implementation lives under `ui_reflex/`.
* Treat it as disposable prototype code rather than an architectural or design constraint.
* It may be substantially refactored or recreated from scratch.

Backend APIs, domain behavior, authorization rules, and data models are the source of truth when redesigning the frontend.

## Development Workflow

Before proposing non-trivial changes:

1. Inspect the relevant existing code.
2. Understand affected interfaces, models, tests, and dependencies.
3. Explain the problem and relevant trade-offs.
4. Propose the smallest coherent solution.
5. Identify how the change should be validated.

Follow the user's global coding-ownership preferences. By default, assist with design, review, debugging, and explanation rather than implementing production code unless implementation is explicitly requested.

Do not perform unrelated cleanup during a focused task.

## Backend Safety

* Preserve account-scoped authorization.
* Do not weaken authentication or authorization for frontend convenience.
* Do not expose global user or financial data.
* Never hard-code credentials or secrets.
* Database schema changes must use Alembic migrations.

## Testing

Use the existing repository test setup documented in `README.md`.

When behavior changes:

* identify relevant tests,
* recommend or add tests when implementation is explicitly delegated,
* run the narrowest relevant tests first,
* broaden validation when appropriate.

Never claim validation succeeded unless it was actually executed.

## Git

Normal development happens on `dev`.

Do not:

* force-push,
* rewrite shared history,
* delete branches,
* merge into `main`,
* or perform other destructive Git operations

without explicit approval.

When giving Git commands, explain what each command does, why it is needed, and the order in which commands should run.

## Product Priorities

Optimize primarily for:

* financial clarity,
* trust,
* explainability,
* low cognitive load,
* practical actionability.

Avoid:

* decorative dashboards without decision value,
* chatbot-first product design,
* premature autonomous agents,
* unnecessary architecture complexity.
