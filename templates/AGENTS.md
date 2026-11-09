# AGENTS.md template

Replace every `<placeholder>` before use.

## Product

- **Name:** `<product>`
- **Purpose:** `<one sentence>`
- **Primary user:** `<user>`
- **Project Brief:** `<path>`
- **Journeys:** `<path>`
- **Acceptance contract:** `<path for Standard or High Assurance; Lean may use the journey catalogue and command list>`

## Commands

- install: `<command>`
- narrow test: `<command>`
- full deterministic suite: `<command>`
- browser journeys: `<command>`
- lint or type check: `<command>`
- build: `<command>`
- dependency audit: `<command>`

## Working rules

- Read the Project Brief and affected journeys before editing.
- Preserve existing conventions and local changes.
- Start behaviour changes with a failing check.
- Use focused characterisation or structural verification for behaviour-preserving adoption.
- Make the smallest coherent implementation change.
- Use deterministic checks as acceptance authority.
- Use model review only for the bounded questions named in the acceptance contract.
- Name the gap before adding a dependency.
- Add abstraction on its second real use.
- Record exact commands or procedures and results.

## Authority boundaries

- unit tests: `<claims>`
- integration tests: `<claims>`
- contract tests: `<claims>`
- browser tests: `<claims>`
- model review: `<claims>`
- human approval: `<claims>`

## Safety boundaries

- credentials: `<handling rule>`
- production data: `<handling rule>`
- external services: `<handling rule>`
- deployment: `<approval rule>`
- destructive changes: `<approval rule>`

## Handoff

Report outcome, changed files, exact commands or procedures and results, evidence paths, remaining risks, and one next action.
