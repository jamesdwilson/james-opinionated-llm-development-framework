# Worked adoption: weekly digest preference

This fictional example shows the cohesive stack applied to an existing Bun web application. Commands and results are illustrative. Its Bugsink integration is a retained historical equivalent, not the current new-install default; see [DIAGNOSTICS.md](../DIAGNOSTICS.md) for the selected OpenTelemetry/SigNoz direction. It is not evidence that either integration has been installed in a consumer.

## Stack map

| Role | Existing or selected tool | Decision |
|---|---|---|
| requirements | Project Brief | add the affected requirements and links |
| BDD | Example Mapping and Given, When, Then | add two journeys |
| TDD and fast tests | Bun test | keep existing |
| browser journeys | Playwright | keep existing |
| bounded UX review | Midscene through a project script | use as advisory because local human agreement is not yet measured |
| error capture | isolated Bugsink project | use synthetic error data |
| supply chain | Bun lockfile, audit, and project release-age policy | keep existing |
| revision and review | clean Git commit and normal pull-request review | keep existing |

## Project Brief extract

| ID | Requirement | Rationale or authority | Acceptance condition | BDD and evidence links |
|---|---|---|---|---|
| R-001 | A signed-in customer can save one weekday. | product owner | Stored preference matches the selected weekday. | J01, V-001 |
| R-002 | Reload displays the stored weekday. | customer workflow | The selected value remains correct after reload. | J01, V-002 |
| R-003 | A failed save preserves the pending choice. | support and recovery requirement | Storage remains unchanged and the selected value remains available for retry. | J02, V-003 |
| R-004 | A controlled failed save sends a synthetic event to the isolated tracker without customer message content, permits retry, and leaves no test residue. | operations and privacy owners | Capture destination, excluded fields, retry, and cleanup all match the requirement. | J02, V-006 |
| Q-001 | The completed state names the active weekday and next delivery. | product owner and support | Both facts are visible after a successful save. | J01, V-004 |

## BDD examples

### J01: successful save

- Given a signed-in customer with Monday stored
- When the customer selects Thursday and saves
- Then Thursday becomes the stored preference
- And reload keeps Thursday selected
- And the completed state names Thursday and the next expected delivery

### J02: failed save

- Given a signed-in customer who selected Thursday
- When the preference service returns a controlled failure
- Then storage remains unchanged
- And Thursday remains selected for retry
- And the synthetic event reaches the isolated tracker without customer message content
- And retry succeeds
- And cleanup removes the synthetic test residue

### UX-Q1: advisory exploration

- Is the next action visually apparent after a successful save?
- This question is exploratory and is not acceptance evidence for Q-001.

## TDD record

**RED**

```text
revision: fictional commit abc1200
bun test test/digest-preferences.service.test.ts
1 failed: controlled failure loses the pending weekday
```

**GREEN**

```text
revision: fictional commit abc1234
bun test test/digest-preferences.service.test.ts
6 passed, 0 failed
```

**REFACTOR**

The form-state update was moved into the existing preference-state module. The focused test remained 6 passed, 0 failed.

## Verification and validation record extract

**Candidate:** fictional clean commit `abc1234`

Each final report records revision `abc1234` and the relevant runtime, browser, or service environment. The RED report remains attached to fictional preimplementation commit `abc1200`.

| ID | Requirement or claim | Purpose | Owner | Procedure or command | Observed result | Evidence |
|---|---|---|---|---|---|---|
| V-001 | R-001 | verification | integration test | `bun test test/digest-preferences.service.test.ts` | 6 passed, 0 failed. | `reports/digest-service-tests.txt` |
| V-002 | R-002 | verification | Playwright | `bunx playwright test e2e/digest-preferences.spec.ts --grep "survives reload"` | 1 passed, 0 failed. | `playwright-report/index.html` |
| V-003 | R-003 | verification | integration and Playwright | run the controlled service failure and failed-save journey | Storage stayed unchanged and Thursday remained selected. | service and browser reports |
| V-004 | Q-001 | verification | Playwright | assert the active weekday and next delivery text | Both required facts were visible. | `playwright-report/index.html` |
| V-005 | UX-Q1 | advisory observation | Midscene | `bun run review:ux digest-preference` | The next action appeared clear. Local human-agreement calibration remains absent. | `midscene_run/digest-preference/report.html` |
| V-006 | R-004 | verification | Bugsink canary | `bun run canary:errors digest-preference` | Synthetic event reached the isolated project; customer message content was absent; retry succeeded; cleanup removed test residue. | `evidence/bugsink-digest-canary.md` |
| V-007 | dependency policy | verification | Bun audit | `bun audit` | No unaccepted advisory. | `evidence/bun-audit.txt` |
| V-008 | dependency admission policy | verification | Bun install and lockfile review | check newly resolved packages, exemptions, and the committed graph | The age gate applied to new resolution; existing lockfile entries were excluded from that claim; no unaccepted exemption remained. | `evidence/bun-admission.md` |

## Evidence limits

- Midscene remains advisory until the project measures agreement with the responsible human reviewer.
- The Bugsink exercise used synthetic data and one controlled service failure.
- `bun audit` checked the resolved graph; the example did not exercise a scoped registry without an advisory endpoint.
- The release-age policy applied only to newly resolved packages and did not retroactively assess existing lockfile entries.
- The focused checks did not evaluate unrelated scheduling behaviour.
- The repository's full pull-request and release process still applies.

## Result

- **Supported claims:** R-001, R-002, R-003, R-004, Q-001
- **Advisory finding:** V-005
- **Unresolved claims:** none within this representative slice
- **Next action:** complete the repository's normal pull-request review and release process
