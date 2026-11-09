# Worked adoption: weekly digest preference

This fictional example shows the Standard profile in a small Bun web application. The commands and results are illustrative.

## Selected profile

**Standard** fits because the preference is customer-visible, stored in the backend, and maintained as production behaviour. The change has a simple rollback and carries no security, privacy, financial, or legal boundary that would trigger High Assurance.

## Files added to the fictional repository

```text
AGENTS.md
docs/NORTH_STAR.md
docs/JOURNEYS.md
docs/ACCEPTANCE.md
test/digest-preferences.test.ts
e2e/digest-preferences.spec.ts
evidence/digest-preferences.md
evidence/digest-preferences-review.md
```

## Product promise

A signed-in customer can choose a weekly digest day, save it, reload the page, and understand when the next digest will arrive.

## Rules

1. Monday through Friday are valid digest days.
2. Save writes one preference for the signed-in account.
3. Reload shows the stored day.
4. A failed save preserves the customer's selected day in the form.
5. The completed state names the selected day and the next expected delivery.

## Examples

### Successful save

- Given a signed-in customer with Monday selected
- When they choose Thursday and save
- Then the page shows Thursday as the active preference
- And the page states the next expected delivery
- And reload keeps Thursday selected

### Failed save

- Given a signed-in customer who selected Thursday
- When the preference service returns a controlled `503`
- Then the page keeps Thursday selected
- And the page offers a retry action
- And the stored preference remains unchanged

## Acceptance split

- unit: valid-day rule and next-delivery calculation;
- integration: account preference write and readback;
- browser: save, reload, failed save, retained selection, and retry;
- model review: whether the completed state makes the selected day and next delivery clear;
- negative control: an isolated fixture that says only “Saved” and receives the expected RED;
- fresh review: stale browser reports, a hidden write failure, and a reload that reads cached state.

## RED first

The first change adds this failing integration case:

```text
controlled 503 keeps the selected day in the form and leaves storage unchanged
```

The implementation then adds retained form state and the retry action.

## Illustrative commands and results

```text
bun test test/digest-preferences.test.ts
4 pass, 0 fail

bun x playwright test e2e/digest-preferences.spec.ts
3 passed, 0 failed

bun audit --json
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
required checks reconciled: 7 of 7
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
- `docs/NORTH_STAR.md`: customer promise and decision boundaries
- `docs/JOURNEYS.md`: save, reload, and recovery examples
- `docs/ACCEPTANCE.md`: required checks and model-review brief
- `test/digest-preferences.test.ts`: rule and persistence checks
- `e2e/digest-preferences.spec.ts`: deterministic browser journey
- `evidence/digest-preferences.md`: candidate, commands, and results
- `evidence/digest-preferences-review.md`: fresh read-only review

### Commands and results
- `bun test test/digest-preferences.test.ts` -> 4 pass, 0 fail
- `bun x playwright test e2e/digest-preferences.spec.ts` -> 3 passed, 0 failed
- `bun audit --json` -> 0 advisories
- independent review -> PASS, 7 of 7 required checks reconciled

### Evidence
- `evidence/digest-preferences.md`: commands, results, and candidate identity
- `evidence/digest-preferences-review.md`: fresh review verdict and counterexamples

### Remaining risk
- The full regression suite still belongs to the repository's existing release workflow.

### Next action
- Add the weekly-digest journey to the existing release workflow.
```
