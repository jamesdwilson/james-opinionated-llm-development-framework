# AGENTS.md template

Replace each placeholder that applies. Unused command lines may be removed. Keep every stack role in the authoritative adoption map with `keep`, `add`, `N/A`, `blocked`, or `not run` plus its reason.

## Product and authorities

- **Product or service:** `<name>`
- **Purpose:** `<one sentence>`
- **Project Brief:** `<path>`
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
- diagnostics and recovery: `<OpenTelemetry / SigNoz Cloud, approved equivalent, or N/A; activation status>`
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
