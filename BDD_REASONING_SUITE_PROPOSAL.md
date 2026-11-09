# Proposed AI-assisted BDD reasoning suite

Status: `proposed_for_review`

## Decision

Adopt Midscene's native `agent.runGherkinScenario()` inside the existing Playwright test project. Call the layer the **Gherkin black-box reasoning suite**.

Do not add Cucumber or `playwright-bdd` yet. Cucumber is useful when product and engineering genuinely share and review full executable specifications, but this lab currently needs a bounded AI reasoning oracle inside an established Playwright runner, not another step-definition framework.[5]

Do not replace deterministic Playwright or the existing structured Midscene observation review:

1. Playwright sets exact fixtures and owns state, API, persistence, permissions, recovery, accessibility mechanics and cleanup.
2. Midscene Gherkin operates and judges a short user-visible scenario.
3. Playwright then verifies the exact resulting state.
4. The existing observer plus structured `aiQuery` remains the holistic trajectory review for purpose, hierarchy, terminology, contradictions and unvisited scope.

This hybrid matches Midscene's supported Playwright integration and preserves the lab's existing ownership boundary.[1]

## Why this is not improvised

Midscene ships a native Gherkin API supporting `Scenario`, `Given`, `When`, `Then`, `And` and `But`; the current installed `@midscene/web` 1.17.4 already contains it.[1][3]

The exact implementation matters:

- `Given` and `When` steps are translated to `aiAct`.
- `Then` steps are translated to `aiAssert`.
- cache is forcibly disabled for scenario actions.
- execution errors identify the semantic step and source line.
- it accepts exactly one optional `Scenario` block.
- it rejects `Feature`, `Rule`, `Background`, `Scenario Outline`, `Examples`, data tables and doc strings.[3]

The public guide says the scenario is executed in one model call, but the published 1.17.7 source iterates over the steps and invokes `aiAct` or `aiAssert` separately for each one.[1][3] We should budget, retry and interpret evidence according to the source behaviour, not the marketing sentence. Keep scenarios short: one rule, one action sequence, one or two visible outcomes.

Midscene also provides a separate YAML test runner, `@midscene/test`, but adding another runner is unnecessary for the first adoption. Its strongest value would be allowing non-TypeScript authors to maintain standalone YAML journeys later.[2][6]

## Model and execution policy

- model: SIWC `gpt-6-sol`
- planning effort: `balance`
- provider reasoning: `low`
- cache: off
- browser: Chromium
- workers: 1
- retries: one bounded retry only for a Midscene-only failure; never retry deterministic Playwright failures
- fixture data: synthetic
- one scenario per test

Midscene's own BDD guide recommends `gpt-6-sol` with `balance` for visual tasks and warns that visual tests are probabilistic.[1] Playwright supports project/test retries, but retries must be reported separately as flaky rather than silently promoted to clean passes.[4]

## Proposed initial suite

The machine-readable catalog is `bdd/JOURNEY_CATALOG.proposed.json`.

### BDD-R01: clear approval rule

Playwright setup: clean store, actor Alex, normal create screen.

Midscene scenario:

```gherkin
Scenario: Create a task that requires another person's approval
  When I create "Wash dishes" so it counts as complete only after another household member approves it
  Then the task should visibly be waiting for another person's approval
  And the next available action should be clear
```

Deterministic twin: assert exact task title, creator, approval rule, status, API record and reload persistence.

### BDD-R02: ambiguous taxonomy negative control

Playwright setup: `/ambiguous`, blank store, title prefilled.

Midscene scenario:

```gherkin
Scenario: Do not guess at an unexplained required choice
  When I try to create "Wash dishes" without guessing what unfamiliar required labels mean
  Then the screen should explain the practical difference before requiring my choice
```

Expected Midscene result: fail at the `Then` assertion. The harness must accept only the expected assertion failure and must also prove deterministically that no task was created. This is the false-green calibration case.

### BDD-R03: creator cannot self-approve

Playwright setup: Alex-created task awaiting another person's approval; actor Alex.

Midscene scenario:

```gherkin
Scenario: The creator cannot approve their own task
  When I inspect the approval controls as Alex
  Then I should not be offered a working self-approval action
  And the screen should explain who must approve next
```

Deterministic twin: exact actor, button state, API status and rejection contract.

### BDD-R04: another actor approves with clear confirmation

Playwright setup: Alex-created task awaiting approval; actor Sam.

Midscene scenario:

```gherkin
Scenario: Another household member approves the task
  When I approve "Wash dishes" as Sam
  Then the task should visibly be complete
  And the screen should make the successful approval unambiguous
```

Deterministic twin: exact approver, status transition, API record and reload persistence.

### BDD-R05: validation recovers after correction

Playwright setup: create screen with an invalid title entered.

Midscene scenario:

```gherkin
Scenario: Correct an invalid task title
  When I replace the invalid title with "Wash dishes"
  Then the stale validation message should disappear
  And I should be able to continue creating the task
```

Deterministic twin: live validation state, submit enabled state and exact created record.

### BDD-R06: visible failure has a working recovery path

Playwright setup: one injected recoverable API failure, then normal service.

Midscene scenario:

```gherkin
Scenario: Recover after a temporary creation failure
  When I create "Wash dishes" and the first attempt fails temporarily
  Then I should see a clear recovery action
  When I use the recovery action
  Then the task should be created without a duplicate
```

Deterministic twin: one failed request, one successful retry, exactly one persisted task and clean error state.

### BDD-R07: North-Star end-to-end sequence

Use this only after R01-R06 are calibrated. Keep Playwright in control of fixture setup and exact persistence checks. Midscene may operate the visible journey and assert clarity, but the existing observation-based J06 remains the authoritative holistic UX review.

## Acceptance rules

The suite is acceptable only when all of these hold:

1. R01, R03-R07 pass twice on the same candidate.
2. R02 fails for the intended visible ambiguity twice.
3. A controlled repair of the ambiguous labels makes R02 pass, proving detection power.
4. Every Midscene scenario has a deterministic Playwright twin for the owned state claim.
5. A Midscene GREEN cannot overrule a deterministic failure.
6. A retry-success is reported as flaky and does not count as a clean repeatability pass.[4]
7. Evidence records scenario ID, exact candidate, prompt text, model, reasoning settings, attempt number, step/line failure and deterministic twin result.
8. Credentials, tokens, DSNs and private content are absent from reports and traces.

## Recommended implementation shape after approval

```text
e2e/
  bdd-reasoning.spec.ts       # Playwright fixtures + runGherkinScenario + exact assertions
bdd/
  scenarios/
    BDD-R01-clear-approval.scenario
    BDD-R02-ambiguous-choice.scenario
    BDD-R03-no-self-approval.scenario
    BDD-R04-other-actor-approval.scenario
    BDD-R05-validation-recovery.scenario
    BDD-R06-temporary-failure-recovery.scenario
  JOURNEY_CATALOG.json
```

Use `.scenario`, not full `.feature`, because Midscene deliberately supports only one restricted scenario and rejects standard Feature/Rule/Outline constructs.[3]

## Sources

[1] https://midscenejs.com/advanced/bdd-style-scripts-with-gherkin.html
[2] https://midscenejs.com/common-test-workflow.html
[3] https://github.com/web-infra-dev/midscene/blob/v1.17.7/packages/core/src/agent/run-gherkin-scenario.ts
[4] https://playwright.dev/docs/test-retries
[5] https://cucumber.io/docs/guides/overview
[6] https://www.npmjs.com/package/@midscene/test
