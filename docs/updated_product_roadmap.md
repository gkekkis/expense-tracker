# Updated Product Roadmap

Date: 2026-06-29

## Executive Direction

The product should evolve from a manual expense tracker into a financial decision platform. The strongest near-term positioning is not a generic budgeting app. The best wedge is a practical cash-flow copilot for freelancers, consultants, solo professionals, and eventually small teams.

The product should answer questions users actively care about:

- Can I safely spend money this week?
- What bills, taxes, or cash-flow risks are coming?
- Which expenses, subscriptions, or behaviors need attention?
- What repeated spending patterns are quietly hurting my goals?
- What action should I take now?
- What would happen if I changed this behavior by 10%, 25%, or 50%?
- What changed since last week?

AI should appear as operational intelligence and action recommendations, not as a chatbot-first feature.

## Target Users

### Primary Initial Segment: Freelancers And Solo Professionals

This segment has a clearer willingness to pay than generic consumers because money management is tied to taxes, invoices, runway, client timing, and business survival.

Key pain points:

- Irregular income makes monthly budgeting unreliable.
- Receipts and expenses are tedious to organize.
- Tax reserves are easy to underfund.
- Deadlines for taxes, insurance, accounting, invoices, and administrative obligations are easy to miss.
- Users need cash-flow clarity before making spending decisions.
- Personal and business expenses often mix.
- Existing tools show data but rarely recommend timely actions.

### Secondary Segment: Shared Households

Shared households are useful for validating multi-member accounts and fair-split logic, but the monetization ceiling may be lower.

Key pain points:

- Shared expenses are difficult to split fairly.
- Recurring bills create recurring disputes.
- Members need visibility without giving everyone full control.

### Later Segment: Small Businesses

Small businesses should come later, after the product proves its intelligence layer with simpler workflows.

Key pain points:

- Cash-flow forecasting.
- Invoice and payment monitoring.
- Reporting.
- Cost optimization.
- Approval workflows.
- Financial document automation.

## Product Positioning

Recommended positioning:

"An AI cash-flow copilot for freelancers and small teams that turns financial data into timely, explainable actions."

Avoid positioning as:

- Another expense tracker.
- A generic budgeting app.
- A chatbot for finance.
- A full accounting replacement at MVP stage.

## Differentiation

The product can stand out by combining:

- Cash-flow decisioning instead of passive dashboards.
- Scheduled pattern detection instead of one-off reports.
- Agentic recommendations with human approval.
- Explainable financial reasoning.
- Personalized recurring-bill, tax, runway, and anomaly logic.
- Deadline, obligation, and opportunity monitoring for professional users.
- Practical workflows around receipts, invoices, exports, and reports.
- Strong privacy, role-based access, and auditability.

AI should be used where it reduces work or improves decisions:

- Categorization.
- Receipt and invoice extraction.
- Pattern detection.
- Recommendation simulation.
- Deadline and obligation monitoring.
- Forecast explanation.
- Recommendation generation.
- Action queue prioritization.

## Pattern Intelligence And Recommendations

This should become a core product capability, not a decorative insight panel.

The product should periodically analyze spending, income, recurring obligations, and user goals, then produce specific recommendations with evidence and estimated impact. For example:

- "You spent EUR X on Friday nights in the last eight weeks. If you reduce this by 25%, your emergency fund date moves forward by Y weeks."
- "Your subscriptions increased by X% since March. Here are the three largest contributors."
- "Your client payments usually arrive around day X, but this month your next bill is due earlier. Keep EUR Y reserved."
- "You are on pace to underfund taxes by EUR X this quarter."

High-value recommendation format:

- Observation: what pattern was detected.
- Evidence: transactions, dates, categories, and trend.
- Impact: cash-flow, tax reserve, runway, goal, or deadline effect.
- Options: realistic actions at different effort levels.
- Confidence: why the system believes this matters.
- User control: dismiss, snooze, accept, mark irrelevant, or turn into an action.

This should start rules-first. AI can help summarize, personalize tone, and explain trade-offs, but the first version should not depend on opaque model reasoning for financial calculations.

## Professional Deadline And Opportunity Intelligence

For freelancers and professionals, the product can become more valuable by monitoring obligations and opportunities, not only expenses.

Useful reminders:

- Tax/VAT/social insurance/accounting filing deadlines.
- Invoice follow-up and payment deadlines.
- Contract renewal or subscription renewal dates.
- Cash reserve deadlines for expected obligations.
- Funding, grant, or subsidy deadlines where eligibility can be inferred from the user's profile.
- Regulatory or law-change alerts that may affect the user's business, tax position, reporting duties, or available benefits.

This capability should be handled carefully:

- It should not pretend to provide legal, tax, or accounting advice without professional review.
- Every external alert should include source, jurisdiction, publication date, applicability assumptions, and confidence.
- User confirmation should be required before acting on anything external or compliance-sensitive.
- The system should prefer "this may affect you; review this source or speak to a professional" over definitive legal conclusions.

The law-change and funding-monitoring idea may justify a separate project or service if it can serve multiple products. My recommendation is to keep it as a separate bounded domain conceptually, but integrate it later through an API or data feed. In this finance app, start with manual/professional calendars and curated deadline templates before building a broad legal-monitoring platform.

## Roadmap Phases

## Phase 0: Stabilized Manual MVP

Objective: Make the current product reliable enough to use manually.

Target users: Founder, pilot users, friendly testers.

Problems addressed:

- Basic account and expense organization.
- Shared account visibility.
- Recurring expenses.
- Budget snapshot.

Features:

- Real account creation with owner membership.
- Expense search and filtering.
- Category selection.
- Multi-currency totals.
- Recurring templates and pending generated expenses.
- Financial profile.
- Basic budget health.
- Member roles.

Technical work:

- Clean repo structure.
- Track dependency and setup files.
- Fix migrations and model mismatches.
- Fix scheduler behavior.
- Enforce backend authorization.
- Stabilize Reflex UI.
- Add root documentation.
- Add CI-ready test commands.

Risks:

- Current pseudo-auth is unsafe.
- UI is temporary.
- Migrations may not upgrade existing data safely.

Success metrics:

- Fresh setup works from README.
- Tests pass.
- A user can create an account, add expenses, see totals, and manage members.

Exit criteria:

- No known critical correctness bugs.
- No global data leaks in API reads.
- A clean branch can be used as the new build base.

## Phase 1: Freelancer Cash-Flow MVP

Objective: Deliver a narrow product that helps freelancers decide what they can safely do with money.

Target users: Freelancers, consultants, solo professionals.

Problems addressed:

- Irregular income.
- Tax reserve planning.
- Upcoming bills.
- Safe-to-spend uncertainty.

Features:

- Safe-to-spend v0.
- Manual or CSV transaction import.
- Upcoming bills from recurring templates.
- Monthly income and irregular income profile.
- Tax reserve estimate.
- Tax and administrative deadline reminders v0.
- Cash runway.
- Weekly financial summary.
- Action inbox with explainable recommendations.
- Scheduled pattern insights with simple impact simulations.

Technical work:

- Import pipeline.
- Transaction normalization.
- Rules-based recommendation engine.
- Notification-ready event model.
- Audit log for recommendations.
- Basic insight evaluation fixtures.
- Deadline calendar model.
- Scheduled insight generation job.

Dependencies:

- Stable transaction model.
- Reliable financial profile.
- Recurring template engine.

Risks:

- Safe-to-spend logic must be trusted.
- Users may not maintain manual data.

Success metrics:

- Users check the Today page at least weekly.
- Users act on recommendations.
- Users mark pattern insights as useful rather than noisy.
- Users avoid or prepare for at least one deadline.
- Users report lower uncertainty about spending.
- At least a small cohort expresses willingness to pay.

Exit criteria:

- 5 to 10 pilot users complete four weekly cycles.
- Safe-to-spend and runway are understandable and trusted.

## Phase 2: Automation And Document Intelligence

Objective: Reduce manual work and improve data quality.

Target users: Paid individual/professional users.

Problems addressed:

- Manual transaction entry.
- Receipt organization.
- Categorization errors.
- Missing tax/accounting records.

Features:

- Receipt OCR.
- PDF/image storage.
- Intelligent transaction categorization.
- Duplicate detection.
- Subscription detection.
- CSV/PDF exports.
- Recommendation confidence and evidence display.

Technical work:

- File storage.
- OCR provider integration.
- Document extraction pipeline.
- Review queue.
- Categorization model or LLM classifier.
- Evaluation set for extraction and classification.
- PII handling and retention policies.

Dependencies:

- Auth and data governance.
- Storage layer.
- Background jobs.

Risks:

- OCR and AI costs.
- Privacy concerns.
- Extraction quality.

Success metrics:

- Reduced manual data-entry time.
- High accepted categorization rate.
- Low correction rate for extracted receipts.

Exit criteria:

- Users import or upload data repeatedly.
- Document intelligence materially improves retention.

## Phase 3: Proactive Financial Intelligence

Objective: Detect risk before the user notices it.

Target users: Pro users and small teams.

Problems addressed:

- Spending drift.
- Cash-flow surprises.
- Underfunded goals or taxes.
- Unusual activity.

Features:

- Anomaly detection.
- Behavioral spending insights.
- Repeated-behavior detection, such as weekly/monthly habit patterns.
- Recommendation impact simulation.
- Predictive burn rate.
- Goal impact analysis.
- Self-adjusting goal projections.
- Cash-flow calendar.
- What changed since last week.
- Notification preferences for alerts, digests, and deadlines.

Technical work:

- Time-series features.
- Baseline and anomaly models.
- Forecasting service module.
- Explanation generation.
- Insight ranking.
- Offline evaluation.
- User feedback loop for accepted, dismissed, irrelevant, and snoozed insights.
- Alert throttling to avoid notification fatigue.

Dependencies:

- Clean historical transaction data.
- User feedback loop.

Risks:

- False positives can destroy trust.
- Insights can become noise.

Success metrics:

- Alert precision.
- Recommendation acceptance.
- Reduced churn among active users.

Exit criteria:

- Users rely on alerts and weekly summary as a habit.

## Phase 4: Agentic Workflows

Objective: Move from recommendations to approved actions.

Target users: Advanced professionals and small businesses.

Problems addressed:

- Repetitive financial operations.
- Receipt matching.
- Invoice follow-up.
- Reporting.
- Cost optimization.

Features:

- Action inbox.
- Agent-generated reports.
- Invoice/payment monitoring.
- Deadline monitoring and reminder escalation.
- Funding opportunity watchlist for eligible users.
- Regulatory/law-change watchlist as a separate bounded capability or external service integration.
- Drafted vendor/client emails.
- Subscription cancellation guidance.
- Tax reserve and transfer recommendations.
- Accounting export workflows.

Technical work:

- Agent orchestration layer.
- Tool registry.
- Approval policy engine.
- Action ledger.
- Rollback/undo where possible.
- Guardrails and output validation.
- Human confirmation for risky actions.

Dependencies:

- Auth.
- Audit logs.
- Integrations.
- Evaluation framework.
- Trusted external data sources for deadlines, funding, and law-change monitoring.

Risks:

- Regulatory boundaries.
- User trust.
- Bad automated actions.

Success metrics:

- Approved actions per active user.
- Time saved.
- Low reversal or complaint rate.

Exit criteria:

- Agents reliably perform bounded workflows with clear evidence and approvals.

## Phase 5: Business Expansion

Objective: Expand into freelancers, startups, and small businesses.

Target users: Small teams, agencies, startups, SMBs.

Problems addressed:

- Business cash-flow forecasting.
- Expense/revenue intelligence.
- Invoice and payment monitoring.
- Reporting.
- Operational alerts.

Features:

- Team roles and approvals.
- Business cash-flow forecast.
- Invoice tracking.
- Revenue and expense intelligence.
- Scenario planning.
- Cost optimization.
- Export to accounting tools.

Technical work:

- Organization model.
- Business entities.
- Integrations.
- More robust workflow engine.
- Observability and SLAs.
- Data retention controls.

Risks:

- Accounting complexity.
- Integration maintenance.
- Support burden.

Success metrics:

- Paid conversion.
- Retention.
- Forecast accuracy.
- Report/export usage.

Exit criteria:

- Business users pay for operational workflows, not just dashboards.

## Features To Remove Or Postpone

Postpone:

- Gamified savings challenges.
- Full bank aggregation before validation.
- Full autonomous agents.
- Broad legal/law-change monitoring before narrow professional deadline validation.
- Business microservices.
- Complex simulations.
- Broad global consumer positioning.

Potentially remove from near-term scope:

- Decorative chatbot UI.
- Generic charts that do not drive decisions.
- Social features not tied to a clear financial outcome.

## Validation Plan

Before expensive features:

- Interview freelancers and solo professionals.
- Run a concierge weekly financial report.
- Test fake-door buttons for safe-to-spend, OCR, anomaly alerts, and tax reserve.
- Run a concierge "Friday pattern" or "weekly leak" report for pilot users.
- Run a concierge professional-deadline calendar for freelancers.
- Test fake-door buttons for funding alerts and law-change alerts before building source monitoring.
- Validate willingness to pay before bank aggregation.
- Use CSV uploads before regulated financial account aggregation.

Critical assumptions:

- Users will share/import financial data if value is clear.
- Safe-to-spend is more valuable than generic budgets.
- Users want specific pattern recommendations more than generic charts.
- Professionals will pay for deadline/opportunity monitoring if alerts are accurate and timely.
- Law-change monitoring is valuable enough to justify a separate service only if source coverage and applicability can be trusted.
- Freelancers will pay for tax/runway clarity.
- Explainable recommendations build trust.

## Recommended Next Product Step

Build the Today page around:

- Safe-to-spend.
- Upcoming bills.
- Month-end projection.
- Tax reserve status.
- Action inbox.
- Pattern insights and recommendation simulations.
- Deadline reminders.
- Recent important transactions.

This page should become the product's identity.
