# Worked adoption: weekly digest preference

This fictional example shows the Standard profile in a small Bun web application. The commands and results are illustrative.

## Selected profile

**Standard** fits because the preference is customer-visible, stored in the backend, and maintained as production behaviour. The change has a simple rollback and carries no security, privacy, financial, or legal boundary that would trigger High Assurance.

## Files added to the fictional repository

```text
AGENTS.md
docs/PROJECT_BRIEF.md
docs/JOURNEYS.md
docs/ACCEPTANCE.md
test/digest-preferences.test.ts
e2e/digest-preferences.spec.ts
evidence/digest-preferences.md
evidence/digest-preferences-review.md
```

## Project brief

- **Purpose:** Let customers control when a weekly digest arrives.
- **Desired outcome:** The saved preference survives reload and clearly states the next delivery.
- **Stakeholders:** Signed-in customers, support staff, and service operators.
- **Operational context:** Account settings page backed by the preference service.
- **Scope:** Weekday selection, save, reload, failed-save recovery, and visible confirmation.

| ID | Type | Requirement | Rationale or source | Acceptance condition | Verification link |
|---|---|---|---|---|---|
| R-001 | behaviour | A customer can choose Monday through Friday and save one active preference. | customer settings request | Readback returns the selected day for the signed-in account. | C01, C02 |
| R-002 | behaviour | Reload shows the stored day. | persistence requirement | Browser reload keeps the saved day selected. | C04 |
| R-003 | recovery | A failed save preserves the selected day in the form. | recovery journey J02 | Controlled `503` leaves storage unchanged and keeps the choice visible. | C03, C05 |
| R-004 | behaviour | The completed state displays the selected day and calculated next delivery. | successful journey J01 | Browser assertions match the stored day and calculated date. | C04 |
| Q-001 | clarity | The customer can understand what changed and what happens next. | customer-support concern | Required product review returns GREEN. | V01, CAL01 |

## Examples

### J01: Successful save

**Requirement IDs:** R-001, R-002, R-004, Q-001

- Given a signed-in customer with Monday selected
- When they choose Thursday and save
- Then the page shows Thursday as the active preference
- And the page states the next expected delivery
- And reload keeps Thursday selected

### J02: Failed save

**Requirement IDs:** R-003

- Given a signed-in customer who selected Thursday
- When the preference service returns a controlled `503`
- Then the page keeps Thursday selected
- And the page offers a retry action
- And the stored preference remains unchanged

## Acceptance links

| Check ID | Requirement IDs | Method | Claim | Evidence |
|---|---|---|---|---|
| C01 | R-001 | unit test | weekday validation accepts Monday through Friday | test report |
| C02 | R-001 | integration test | save writes one preference and readback returns it | test report |
| C03 | R-003 | integration test | controlled `503` leaves storage unchanged | test report |
| C04 | R-002, R-004 | browser test | save and reload show the exact stored day and calculated delivery date | Playwright report |
| C05 | R-003 | browser test | failed save retains the selected day and exposes retry | Playwright report |
| V01 | Q-001 | bounded model review | the completed state clearly explains what changed and what happens next | model-review record |
| CAL01 | Q-001 | calibration review | the isolated “Saved” fixture receives the expected RED | calibration record |
| S01 | dependency policy | audit | the resolved dependency graph has no unaccepted advisory | audit report |
| R01 | all | fresh read-only review | candidate, evidence, and counterexamples reconcile | review report |

## RED first

The first change adds this failing integration case:

```text
controlled 503 keeps the selected day in the form and leaves storage unchanged
```

The implementation then adds retained form state and the retry action.

## Illustrative commands and results

```text
bun test test/digest-preferences.test.ts  # C01-C03
4 pass, 0 fail

bun x playwright test e2e/digest-preferences.spec.ts  # C04-C05
3 passed, 0 failed

bun audit --json  # S01
0 advisories
```

The model-review record contains:

```json
{
  "verdict": "GREEN",
  "stopped_at": "completed_goal",
  "evidence": [
    "The page names Thursday as the active digest day.",
    "The page shows the next expected delivery date."
  ],
  "reason": "The saved state answers what changed and what happens next."
}
```

The isolated negative control returns:

```json
{
  "verdict": "RED",
  "stopped_at": "unclear_saved_state",
  "evidence": ["The page says Saved without naming the active day."],
  "reason": "The customer cannot verify the selected preference."
}
```

## Illustrative independent review

The fresh read-only reviewer recomputes candidate `abc1234`, checks each required report, and attempts three counterexamples: stale browser output, a hidden write failure, and reload from cached client state.

```text
verdict: PASS
candidate: abc1234
eight pre-review checks reconciled: 8 of 8
unresolved release blockers: 0
report: evidence/digest-preferences-review.md
```

## Illustrative handoff

```markdown
## Adoption result

**Profile:** Standard
**Outcome:** PASS for the representative weekly-digest slice
**Candidate:** clean commit abc1234

### Changed files
- `AGENTS.md`: project commands and authority rules
- `docs/PROJECT_BRIEF.md`: purpose, stakeholders, requirements, constraints, and acceptance links
- `docs/JOURNEYS.md`: save, reload, and recovery examples
- `docs/ACCEPTANCE.md`: required checks and model-review brief
- `test/digest-preferences.test.ts`: rule and persistence checks
- `e2e/digest-preferences.spec.ts`: deterministic browser journey
- `evidence/digest-preferences.md`: candidate, commands, and results
- `evidence/digest-preferences-review.md`: fresh read-only review

### Checks and results
- C01-C03: `bun test test/digest-preferences.test.ts` -> 4 pass, 0 fail
- C04-C05: `bun x playwright test e2e/digest-preferences.spec.ts` -> 3 passed, 0 failed
- V01: model review -> GREEN, `completed_goal`
- CAL01: negative control -> RED, `unclear_saved_state`
- S01: `bun audit --json` -> 0 advisories
- R01: independent review -> PASS, 8 of 8 pre-review checks reconciled

### Evidence
- `evidence/digest-preferences.md`: commands, results, and candidate identity
- `evidence/digest-preferences-review.md`: fresh review verdict and counterexamples

### Traceability
- R-001 -> J01 -> C01, C02
- R-002 -> J01 -> C04
- R-003 -> J02 -> C03, C05
- R-004 -> J01 -> C04
- Q-001 -> J01 -> V01, CAL01

### Remaining risk
- The full regression suite still belongs to the repository's existing release workflow.

### Next action
- Add the weekly-digest journey to the existing release workflow.
```
