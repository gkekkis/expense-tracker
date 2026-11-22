# Technical Roadmap

Date: 2026-08-29

Status: Authoritative technical direction supporting `docs/updated_product_roadmap.md`.

## Current Baseline

The repository is a Python modular monolith with:

- FastAPI, Pydantic 2, SQLAlchemy, PostgreSQL, and Alembic;
- APScheduler for current scheduled work;
- no frontend in the working tree: the Reflex 0.8 prototype was removed on 2026-11-22 and remains in the git history;
- signed bearer-token authentication, account-scoped authorization helpers, and audit logging;
- a tracked backend Dockerfile;
- GitHub Actions jobs for Ruff, pytest, and migration smoke testing;
- a PostgreSQL-backed pytest suite;
- a manually verified Azure development backend foundation: Azure Container Registry, Container Apps and Log Analytics, PostgreSQL Flexible Server, Key Vault, a user-assigned managed identity, explicit Alembic migration execution, and an HTTPS FastAPI health check.

Verification on 2026-08-29: `uv run pytest -q` completed with 50 passing tests.

The current backend supports users, accounts, memberships, expenses, categories, recurring templates, currency normalization, financial profiles, and budget summaries. It does not yet support trustworthy safe-to-spend, income streams, tax reserves, runway, insights, opportunities, or edition-aware workspaces.

## Immediate Constraints

- There is no frontend until the rebuild; the new frontend must use the bearer-token API, and the budget summary is not safe-to-spend.
- The existing Dockerfile packages only FastAPI; frontend production build and hosting are not configured.
- CI validates code and migrations but does not deploy an environment or run browser smoke tests.
- The Azure backend foundation is configured manually rather than as infrastructure as code. A repeatable deployment workflow, backup/restore exercise, and rollback procedure are still absent from the repository.
- APScheduler currently runs inside the FastAPI web process. With scale-to-zero, scheduled work is not dependable; retain one API replica at most for this development spike and do not rely on scheduled processing until it is moved to an appropriate worker/job design.
- VIEWER write protection and the remaining authorization matrix must be verified before inviting external testers.

## Technical Principles

- Keep a modular monolith until validated load or ownership boundaries require extraction.
- Keep backend APIs, authorization, and financial calculations authoritative.
- Prefer explicit domain modules and typed contracts over generic framework abstractions.
- Make financial and eligibility results reproducible, explainable, and testable.
- Keep Personal and Professional in one platform without scattering edition checks through the codebase.
- Use managed services where they remove meaningful solo-maintainer operational work.
- Deliver small vertical slices that remain deployable.
- Do not add Redis, queues, object storage, OCR, or agent orchestration before the active phase needs them.

## Platform Domain Direction

The long-term domain separates four concepts:

- **Identity:** the authenticated person.
- **Workspace:** an account-scoped financial context with members and roles.
- **Edition:** Personal or Professional applicability.
- **Entitlement:** tier, jurisdiction, rollout, and role-based access to a capability.

The backend should eventually resolve named capabilities, for example:

- `transactions.manage`;
- `members.manage`;
- `planning.professional`;
- `planning.personal`;
- `opportunities.personal`;
- `opportunities.professional`;
- `eligibility.automated`.

Capability checks complement rather than replace authorization. The backend enforces both. The UI uses the resolved capabilities to compose navigation and page sections; hiding a control is never a security boundary.

Introduce only the minimum workspace-edition persistence needed for Phase 1 onboarding and composition. Keep it on the current Account boundary unless implementation analysis proves that a broader workspace model is already necessary. Any schema change requires an explicit domain decision and Alembic migration; tier entitlements and a full capability system remain later work.

## Frontend Architecture

### Stack Decision

**Update 2026-11-22:** the founder decided to rebuild the frontend from scratch, starting from a new design, rather than evolve the Reflex prototype. The stack is open again: the first frontend design document will choose between Reflex and the React and TypeScript SPA described below, and this section will then be rewritten. The Reflex prototype itself was removed from the working tree on 2026-11-22 and remains in the git history. Until the stack decision, the Reflex-specific guidance in this section, in "Reflex Structure", in the Azure deployment target, and in the Phase 1 required work describes the previous plan.

Previous plan: retain Reflex through the Phase 1 product shell and evaluate it against real workflows in Phase 2. Product uncertainty is currently more important than frontend scale, and staying in Python reduces delivery overhead for the solo maintainer.

Reflex is conditional rather than permanent. Reconsider it if repeated evidence shows that:

- dense transaction review or keyboard workflows require excessive custom wrappers;
- routine interactions suffer from server event and WebSocket round trips;
- responsive behavior requires duplicated page implementations;
- accessibility or browser testing cannot be enforced reliably;
- Reflex deployment/state operations become disproportionate;
- two consecutive meaningful features take materially more effort than a React implementation would.

If migration is justified, prefer a React and TypeScript SPA built with Vite, React Router, and a server-state library. The authenticated product does not currently require a second application backend or Next.js server rendering.

### Information Architecture

Use five stable product areas:

- Today;
- Transactions;
- Plan;
- Inbox;
- Settings.

The edition changes page composition and capabilities, not the overall visual language. Account and member administration live under Settings rather than competing with daily work.

### Reflex Structure

Evolve the prototype toward feature ownership:

```text
ui_reflex/ui_reflex/
|-- pages/
|-- features/
|   |-- today/
|   |-- transactions/
|   |-- planning/
|   |-- inbox/
|   `-- account_management/
|-- components/
|   |-- primitives/
|   |-- finance/
|   |-- feedback/
|   `-- shell/
|-- state/
|-- services/
|-- contracts/
`-- theme/
```

Use mostly flat page or feature states. Keep only minimal session and account context shared. Store access tokens and other sensitive values in backend-only Reflex variables. Replace `Dict[str, Any]` at API boundaries with typed response models. Loading, error, empty, and success state belongs to each operation or section rather than one application-wide flag.

The Reflex API client should own:

- base URL and timeout configuration;
- bearer authorization;
- 401/session-expiry handling;
- typed response conversion;
- safe error normalization;
- correlation information where supported.

Financial calculations remain FastAPI contracts. The UI must not independently derive safe-to-spend, tax reserves, eligibility, or other trusted headline values.

## Initial Azure Deployment Target

Phase 1 should first prove this small topology:

```text
Browser
  |-- static Reflex frontend -> Azure Static Web Apps
  |-- Reflex events/WebSocket -> Azure Container Apps
  `-- product API requests (through Reflex state) -> FastAPI on Azure Container Apps

FastAPI -> Azure Database for PostgreSQL Flexible Server
Secrets -> Azure Key Vault references / Container Apps managed identity
Images -> Azure Container Registry
Logs and metrics -> Azure Monitor / Log Analytics
CI/CD -> GitHub Actions
```

Why this target:

- Reflex supports exporting frontend and backend separately and depends on WebSockets for events.
- Azure Container Apps supports WebSocket ingress and container revisions without requiring Kubernetes administration.
- Azure Static Web Apps can publish the generated static frontend.
- PostgreSQL Flexible Server provides managed backups, TLS, patching, and a burstable development tier.

The FastAPI, PostgreSQL, managed-identity, Key Vault, migration, HTTPS-health, Container Apps HTTP probes, and startup-log portions of this topology were manually proven in the development subscription on 2026-08-30. Reflex export, WebSocket connectivity, frontend/API CORS, backup/restore, rollback, infrastructure as code, and CI/CD remain unproven. Complete that thin spike before investing heavily in the redesigned UI.

For the private draft:

- use one region close to the initial users;
- use the smallest suitable non-production resources;
- keep one Reflex backend replica if in-memory state is used;
- do not scale the Reflex backend horizontally without a shared state manager such as Redis;
- require TLS and narrow allowed origins;
- keep secrets out of images, source control, workflow logs, and frontend state;
- execute Alembic as a deliberate deployment step, not on every arbitrary process start;
- document backup retention and perform at least one restore exercise before external pilot data matters.

Redis is not required for the founder-only draft if Reflex runs as a single replica and session loss on restart is accepted. Add a managed Redis-compatible state store only when availability or horizontal scaling justifies it.

## Technical Execution By Product Phase

### Phase 1 - Deployable Shared Platform Draft

Technical outcome: secure vertical deployment and a maintainable shared shell, with Personal/Household implemented as the first acceptance path and a basic Professional composition.

Required work:

- complete the endpoint/role authorization matrix, especially VIEWER writes;
- move the UI to bearer authentication and `/auth/me`;
- design and migrate the minimal Account edition field and edition-aware onboarding contract;
- split the Reflex state and introduce typed API contracts;
- build shared Today, Transactions, Plan, Inbox, and Settings shell behavior;
- implement the Personal/Household composition first, then the basic Professional composition from shared components;
- retain truthful budget and recurring information without future financial claims;
- create Reflex production build/container configuration and infrastructure as code;
- add GitHub Actions deployment after CI succeeds;
- add browser smoke coverage for login and the main manual flow;
- configure Azure health checks, structured logs, secrets, and database backups;
- write a private-release and rollback checklist.

### Phase 2 - Personal And Household Decision MVP

Technical outcome: trusted household decisions from normalized manual and CSV data, with clearer shared responsibility and a curated benefit/voucher foundation.

Required work:

- add household income and import models, review staging, normalization, and duplicate detection;
- implement available-to-spend, goals, reserves, upcoming bills, and shared-responsibility services;
- store calculation inputs, period, assumptions, result, and evidence;
- create an insight/action-inbox model with accept, dismiss, snooze, and irrelevant feedback;
- add a curated Greek household benefit/voucher model with source and manual eligibility metadata;
- add unit fixtures for household formulas and integration fixtures for imports and scheduled results.

### Phase 3 - Professional Decision MVP

Technical outcome: trusted Professional cash-flow decisions and professional opportunities on the already edition-aware platform.

Required work:

- extend profiles for irregular income, professional obligations, and relevant jurisdiction data;
- implement safe-to-spend or safe-to-pay-yourself, tax reserve, runway, and upcoming-obligation services;
- add the minimum invoice/client-payment model required by cash-flow decisions;
- add a centralized capability resolver and initial entitlement contract;
- support safe switching between workspace contexts;
- extend the shared opportunity model with professional grants, funding, deadlines, and audience rules;
- test cross-edition visibility, cross-workspace isolation, and capability enforcement.

### Phase 4 - Trusted Automation And Full Rollout

Technical outcome: operationally support paid editions and evidence-backed automation.

Possible work admitted by validated demand:

- object storage and document processing;
- worker queues for durable scheduled or long-running work;
- categorization and extraction evaluation datasets;
- automated eligibility rules and versioned source snapshots;
- notification delivery, billing, retention, deletion, and support tooling;
- recommendation quality monitoring and alert throttling;
- approval policy, action ledger, output validation, and rollback before agent actions;
- service extraction only where scaling or operational isolation proves necessary.

## Testing And Release Gates

Every behavior change should begin with the narrowest relevant test and expand according to risk.

Before the Phase 1 Azure draft:

- Ruff, pytest, and fresh-database migration jobs pass in CI;
- authentication and account-scoping tests cover every exposed resource family;
- a production-mode frontend build succeeds;
- browser smoke tests cover login, account entry, expense creation/search, and sign-out;
- deployment health checks pass and logs contain no secrets;
- migration, rollback, backup, and restore procedures are documented and exercised proportionally to the private-draft risk.

Later phases add:

- golden files for CSV imports and exports;
- deterministic fixtures for financial calculations and recommendations;
- source and eligibility evaluation fixtures;
- frontend accessibility and responsive checks;
- end-to-end tests for approved external actions.

Never treat generated prose as evidence that a financial, tax, or eligibility calculation is correct.

## Security And Governance Gates

Before any non-local deployment:

- disable `X-User-Id` authentication;
- enforce account and role authorization server-side;
- configure narrow CORS origins and TLS;
- keep credentials in managed secret storage;
- prevent sensitive values from entering frontend state or logs.

Before external pilot users:

- define data deletion/export expectations and a minimal privacy statement;
- verify backup/restore behavior;
- audit sensitive mutations and recommendation feedback;
- define how security issues and incorrect financial results are reported.

Before opportunity or regulatory intelligence:

- store authoritative source, jurisdiction, publication/effective dates, freshness, audience, and applicability assumptions;
- provide non-advice language and human review for high-risk information;
- prevent cross-edition alerts and unsupported eligibility claims.

Before agents or external actions:

- require explicit approval policies, an action ledger, evidence, failure handling, and rollback where possible.

## Immediate Technical Sequence

Only Phase 1 is active:

1. run the Azure deployment spike;
2. close remaining authorization and UI-authentication gaps;
3. add the minimal edition-aware Account contract and onboarding;
4. refactor the UI state only as needed to build and validate Personal/Household first, then the basic Professional composition;
5. automate deployment and complete the private-release gate.

## External Platform References

- Azure Container Apps ingress and WebSocket support: <https://learn.microsoft.com/azure/container-apps/ingress-overview>
- Azure Container Apps deployment from source: <https://learn.microsoft.com/azure/container-apps/containerapp-up>
- Azure Container Apps secrets and Key Vault references: <https://learn.microsoft.com/azure/container-apps/manage-secrets>
- Azure Database for PostgreSQL Flexible Server: <https://learn.microsoft.com/azure/postgresql/flexible-server/overview>
- Azure Static Web Apps: <https://learn.microsoft.com/azure/static-web-apps/>
- Reflex self-hosting and export: <https://reflex.dev/docs/hosting/self-hosting/>
- Reflex runtime and state architecture: <https://reflex.dev/docs/advanced-onboarding/how-reflex-works/>
