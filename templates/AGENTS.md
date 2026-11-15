# AGENTS.md template

Replace each placeholder that applies. Unused command lines may be removed. Keep every stack role in the authoritative adoption map with `keep`, `add`, `N/A`, `blocked`, or `not run` plus its reason.

## Product and authorities

- **Product or service:** `<name>`
- **Purpose:** `<one sentence>`
- **Project Brief:** `<path; reuse the current authoritative brief or North Star>`
- **Compass:** `<current brief authority/version: users, outcome, desired experience and exclusions>`
- **BDD journeys:** `<path>`
- **Verification and validation record:** `<path>`
- **Authoritative adoption stack map:** `<path>`
- **Product authority:** `<owner or document>`
- **Technical authorities:** `<schemas, interfaces, policies, or source paths>`

## Stack map

- requirements and BDD: `<paths and practice>`
- runtime and fast tests: `<Bun or existing equivalent>`
- integration and contract checks: `<commands>`
- browser journeys: `<Playwright or existing equivalent>`
- bounded UX review: `<Midscene, human review, validated equivalent, or N/A>`
- diagnostics and recovery: `<GlitchTip + MCP: local default or explicit cloud choice; approved equivalent or N/A; activation status>`
- supply-chain checks: `<commands and policy>`
- candidate identity and review: `<project-native process>`

Missing authorization, unavailable tooling, or an unexecuted required role is `blocked` or `not run`, not N/A. Use N/A only when the product and authorised scope make the role genuinely inapplicable.

## Commands

- setup: `<command>`
- focused test: `<command>`
- broader deterministic checks: `<command>`
- browser journeys: `<command>`
- bounded UX review: `<command or N/A>`
- error canary and recovery: `<command or N/A>`
- dependency audit: `<command>`
- build or packaging: `<command>`

## Working rules

- Read the affected requirements and BDD examples before editing.
- Select a batch that advances the current compass or removes a demonstrated blocker to it. State its contribution, sufficient evidence and stopping condition in the existing task; do not add a separate ledger.
- After a handback, interruption or compaction, reconcile that same compass, accepted results and next eligible action. Do not repeat unchanged green checks or restart product discovery without a material reason.
- Repair concrete findings and rerun affected evidence. Stop when the agreed claims are supported; change scope through the responsible authority rather than moving the finish line.
- Keep optional-tool and criterion-specific blockers scoped. A missing Midscene integration is not a reason to stop independent acceptance; actual failures, refusals and protected-action permissions still apply.
- Distinguish measured research, stakeholder intent, field experience, assumptions and chosen engineering policy. Do not invent research support for a practical rule.
- Identify consequential ambiguity and seek clarification from the responsible authority.
- Use RED, GREEN, REFACTOR for changed behaviour.
- Use a verified characterisation baseline for behaviour-preserving work.
- Keep deterministic checks responsible for computable behaviour.
- Keep Midscene within its declared visual questions and validation status.
- Use synthetic data and isolation for diagnostic exercises. Honour both opt-out variables and never activate uploads merely by adopting the framework.
- Follow the repository's authorization, security, review, and release rules.
- Record observed results and evidence limits.

## Approval boundaries

- dependencies: `<rule>`
- credentials and sensitive data: `<rule>`
- external services: `<rule>`
- deployment and release: `<rule>`
- destructive or irreversible work: `<rule>`

## Result

Report the stack map, affected requirements, changed files, commands and procedures, observed results, evidence locations, substitutions, and unresolved risks.
