# Product Rollout Roadmap

Date: 2026-08-29

Status: Authoritative product direction and rollout north star.

The implementation architecture and technical gates are documented in `docs/technical_roadmap.md`.

## North Star

Build one financial decision platform with two focused editions:

- **Personal** for individuals and shared households.
- **Professional** for freelancers, consultants, solo professionals, and eventually small teams.

The product should turn financial data into timely, explainable actions. It is not intended to be another passive expense dashboard, a chatbot-first finance product, or a full accounting replacement.

Chronological delivery gives Personal and shared households a slight priority so the founder can test the product continuously with real data. Professional remains the intended commercial wedge and follows on the same platform rather than in a second codebase.

## Product Model

### Identity And Workspaces

A user is a person with one identity. A workspace is the financial context in which the person is operating.

A user may eventually belong to more than one workspace, for example:

- an individual Personal workspace;
- a shared Personal workspace with household members;
- a Professional workspace with an accountant or collaborator.

Personal and household use do not need separate editions. Household behavior is collaboration within the Personal edition. Edition and collaboration are separate concepts:

- `PERSONAL` or `PROFESSIONAL` determines the relevant product capabilities;
- individual or shared membership determines who participates and what each member may do.

The current backend `Account` remains the source of truth until a workspace model is deliberately designed and migrated with Alembic.

### Shared Platform Capabilities

Both editions can reuse:

- identity, authentication, accounts, memberships, and roles;
- transactions, categories, recurring items, and currency normalization;
- goals, reserves, imports, exports, and notifications;
- explainable recommendations and feedback;
- opportunity ingestion, source provenance, deadlines, and eligibility criteria;
- privacy, authorization, audit history, and human approval controls.

### Edition-Specific Capabilities

Personal focuses on:

- household safe-to-spend and bill coverage;
- savings goals and shared spending;
- fair contribution and responsibility views;
- household benefits, subsidies, and vouchers.

Professional focuses on:

- irregular income, cash runway, and safe-to-pay-yourself decisions;
- tax reserves and professional obligations;
- invoices, client payment timing, and business expenses;
- professional grants, subsidies, and funding opportunities.

An irrelevant capability must not appear merely because a user has a higher subscription tier. Applicability and commercial entitlement are separate checks:

1. Is the capability relevant to this edition?
2. Is it supported for this jurisdiction and profile?
3. Does the workspace's tier include it?

Pricing and tier names are intentionally deferred until pilot value is validated.

## Product Experience

### Shared Information Architecture

Both editions use the same calm, decision-oriented shell:

1. **Today** - current position, upcoming risks, and the next useful actions.
2. **Transactions** - capture, search, review, categorize, and approve.
3. **Plan** - cash flow, recurring obligations, reserves, and goals.
4. **Inbox** - recommendations, deadlines, warnings, and approvals.
5. **Settings** - workspaces, members, profile, currency, preferences, and security.

Accounts and members are administrative context rather than primary daily destinations. Desktop is the efficient working surface; mobile prioritizes quick checking, capture, and review.

### Today By Edition

Professional Today eventually prioritizes:

- safe to spend or safe to pay yourself;
- upcoming bills and expected income;
- tax reserve and runway;
- overdue invoices and professional deadlines;
- a short action inbox;
- transactions requiring review.

Personal Today eventually prioritizes:

- available household money and upcoming bills;
- savings and reserve progress;
- shared expenses requiring review;
- household benefit or voucher deadlines;
- a short action inbox;
- recent important activity.

The UI must never overstate what the backend currently calculates. Until a trusted safe-to-spend contract exists, the initial Today page must use truthful labels such as **Budget snapshot** or **Available this month**.

### Design Principles

- Practicality and decision value take priority over decoration.
- Important figures must explain their period, inputs, freshness, and next action.
- Financial calculations belong to tested backend services; the UI presents and explains them.
- Use charts only when they clarify a decision, trend, or future risk.
- Use plain language, consistent money formatting, accessible status colors, and clear empty states.
- Start recommendations with deterministic rules. AI may summarize or personalize only after the underlying result is reproducible.
- Require human confirmation for external, financial, legal, tax, or compliance-sensitive actions.

## Opportunity And Eligibility Intelligence

Opportunity intelligence is a shared platform capability with edition-specific targeting.

The common pipeline should eventually support:

1. ingesting or curating an authoritative source;
2. recording jurisdiction, audience, dates, criteria, and source freshness;
3. classifying the opportunity for Personal, Professional, or both;
4. matching it against the appropriate profile;
5. presenting evidence, assumptions, confidence, and next steps;
6. recording saved, dismissed, irrelevant, and applied feedback.

For Greece, the same infrastructure may serve household vouchers and professional grants, but the audience rules and UI language must remain distinct. Freelancer tax updates belong only to Professional. Household benefits belong only to Personal.

Begin with curated opportunities and manual eligibility guidance. Automated eligibility assessment is a possible higher-tier capability only after source quality, profile data, and criteria evaluation have been validated. The product must not present legal, tax, or eligibility conclusions as guaranteed outcomes.

## Four-Phase Rollout

Dates after Phase 1 are directional and must be reviewed at each phase gate. The plan assumes one human owner supported by agents, not a staffed product team.

### Phase 1 - Deployable Shared Platform Draft

Target: now through **2026-12-31**.

Outcome: a secure, private platform draft is deployed on Azure with Personal/Household as the first acceptance path and a basic Professional path on the same shared foundation.

In scope:

- close remaining authorization, role, migration, and deployment blockers;
- replace the UI's prototype authentication with the backend bearer-token flow;
- add a minimal workspace edition choice for Personal or Professional;
- build the responsive product shell and edition-appropriate initial Today pages;
- retain practical transaction, recurring-item, profile, account, and member workflows;
- test Personal and shared-household workflows first with the founder's real usage;
- expose the same truthful manual foundation to Professional without advanced professional claims;
- show only backend-supported budget and upcoming-item information;
- add deployment configuration, secrets handling, logs, health checks, and repeatable CI/CD;
- deploy FastAPI, Reflex, and PostgreSQL to a private Azure environment.

Explicitly out of scope:

- genuine safe-to-spend, tax reserve, or runway claims;
- CSV import, OCR, bank aggregation, automated opportunity ingestion, or agents;
- production billing, broad public onboarding, or production-grade scale.

Exit gate:

- a live Azure URL is available to the founder and invited testers;
- onboarding can create or enter Personal and Professional workspace contexts;
- login, account selection, expense creation/search, recurring review, budget snapshot, and sign-out work end to end;
- the founder can use the Personal/Household path repeatedly without encountering Professional-only language;
- non-local environments do not permit `X-User-Id` authentication;
- CI, migrations, health checks, logs, and database backup behavior are verified;
- no known critical account-scoping or financial-correctness defect remains;
- known product limitations are visible and honestly labeled.

### Phase 2 - Personal And Household Decision MVP

Directional target: first half of 2027.

Outcome: the founder and a small Personal/Household cohort use the product through repeated financial cycles and can judge whether its decisions reduce everyday uncertainty.

In scope:

- manual and CSV transaction import with review and duplicate handling;
- household income, available-to-spend v0, upcoming bills, goals, and reserves;
- clearer shared contributions, responsibility, and member review flows;
- a rules-first action inbox with evidence and feedback;
- weekly summaries;
- a small curated Greek household benefit and voucher catalogue with manual eligibility guidance;
- concise exports needed for household review.

Exit gate:

- pilot users understand how the headline figures are calculated;
- users return weekly and act on or meaningfully dismiss recommendations;
- available-to-spend and shared-responsibility calculations have fixtures and explainable evidence;
- at least a small cohort reports reduced uncertainty and repeated practical value.

### Phase 3 - Professional Decision MVP

Directional target: second half of 2027, after the Personal/Household decision gate.

Outcome: freelancers use the Professional edition through at least four weekly financial cycles while the validated Personal/Household edition remains available.

In scope:

- irregular-income modeling, safe-to-spend or safe-to-pay-yourself, tax reserve, runway, and upcoming obligations;
- invoice and client-payment tracking at the minimum level required for cash-flow decisions;
- a Professional action inbox, weekly summary, and curated Greek professional deadlines;
- extension of the shared opportunity model from household benefits to professional grants and funding;
- edition-aware profile matching and manual eligibility guidance;
- limited tier experiments based on demonstrated value.

Exit gate:

- freelancers understand and trust the Professional headline calculations;
- Personal and Professional users see only relevant workflows and opportunities;
- one identity can safely participate in multiple workspace contexts;
- both editions reuse shared platform capabilities without scattered edition conditionals;
- at least a small Professional cohort reports reduced uncertainty and willingness to pay.

### Phase 4 - Trusted Automation And Full Rollout

Target: evidence-gated; no committed date.

Outcome: both editions can support paid rollout with useful automation and bounded, auditable intelligence.

Candidate scope, admitted only by evidence:

- receipt and document extraction, categorization assistance, and review queues;
- richer invoice and client-payment workflows for Professional;
- automated eligibility assessment for supported opportunities;
- proactive pattern, anomaly, and deadline intelligence;
- billing, tier enforcement, data export/deletion, retention controls, and operational support;
- bank or accounting integrations where manual/CSV workflows have proven recurring demand;
- approved agent actions only after policy, evidence, audit, and rollback foundations exist.

Exit gate:

- paid users repeatedly receive measurable decision value or time savings;
- recommendation and eligibility quality can be evaluated and monitored;
- privacy, security, data lifecycle, support, and reliability are ready for the intended audience;
- automated actions remain bounded, explainable, and reversible where possible.

## Scope Discipline

To keep the roadmap executable:

- only one phase is active at a time;
- Personal/Household is the first acceptance path in Phase 1 and the only edition receiving deep decision features in Phase 2;
- Professional receives the shared Phase 1 foundation, then becomes the decision-feature focus in Phase 3;
- keep at most three active workstreams: product, reliability/security, and deployment;
- every feature must support the current phase outcome or remain in the backlog;
- every phase must leave a deployable, testable product;
- agents may accelerate bounded research, implementation, review, testing, and documentation, but product decisions and release acceptance remain human-owned;
- do not expand scope merely because agent capacity is available.

## Deferred Until Evidence Requires Them

- broad global consumer positioning;
- full bank aggregation;
- broad legal or law-change monitoring;
- autonomous agents;
- microservices;
- complex simulations;
- decorative dashboards, social features, and gamification without decision value;
- small-business accounting replacement.

## Immediate Focus

Phase 1 is the only current commitment. The next planning unit should be a short sequence of deployable vertical slices:

1. prove the Reflex/FastAPI/PostgreSQL Azure topology;
2. complete secure UI authentication and introduce the minimal edition-aware workspace context;
3. build the Personal/Household shell and truthful Today page first;
4. add the basic Professional composition on the same shared components;
5. harden the manual workflows, automate deployment, and run the private-release checklist.
