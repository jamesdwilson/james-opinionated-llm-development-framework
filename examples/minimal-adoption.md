# Worked adoption: weekly digest preference

This fictional example shows the minimal playbook applied to an existing web application. Tool names and commands belong to the fictional repository.

## Files added

```text
AGENTS.md
docs/PROJECT_BRIEF.md
docs/VERIFICATION.md
```

A separate journey catalogue was unnecessary because two short scenarios fit in the Project Brief.

## Project Brief extract

### Purpose

Let signed-in customers choose the weekday for a weekly digest.

### Requirements

| ID | Requirement | Rationale or authority | Acceptance condition | Evidence link |
|---|---|---|---|---|
| R-001 | A signed-in customer can save one weekday. | product owner | The stored preference matches the selected weekday. | V-001 |
| R-002 | Reload displays the stored weekday. | customer workflow | The selected value remains correct after reload. | V-002 |
| R-003 | A failed save preserves the customer's pending choice. | support and recovery requirement | A controlled failed save leaves storage unchanged and keeps the selected value visible. | V-003 |
| Q-001 | The completed state states the active weekday and next expected delivery. | product owner and support | Inspection confirms both facts are visible. | V-004 |

### Representative scenarios

**Successful save**

- Given a signed-in customer with Monday stored
- When the customer selects Thursday and saves
- Then Thursday is stored and remains selected after reload
- And the completed state shows Thursday and the next expected delivery

**Failed save**

- Given a signed-in customer who selected Thursday
- When the preference service returns a controlled failure
- Then storage remains unchanged
- And Thursday remains selected for another attempt

## Verification and validation record extract

**Subject:** weekly digest preference change
**Reference:** fictional commit `abc1234`

| ID | Requirement or claim | Purpose | Method | Procedure or command | Expected result | Observed result | Evidence |
|---|---|---|---|---|---|---|---|
| V-001 | R-001 | verification | testing | `npm test -- digest-preferences.service.test.ts` | Stored weekday matches the request. | 6 passed, 0 failed. | `reports/digest-service-tests.txt` |
| V-002 | R-002 | verification | testing | `npm run test:e2e -- digest-preferences.spec.ts --grep "survives reload"` | Reload shows the stored weekday. | 1 passed, 0 failed. | `reports/digest-reload/index.html` |
| V-003 | R-003 | verification | testing | run the service failure fixture and `npm run test:e2e -- digest-preferences.spec.ts --grep "failed save"` | Storage stays unchanged and the pending choice remains visible. | Service and browser checks passed. | `reports/digest-failure-tests.txt`, `reports/digest-failure/index.html` |
| V-004 | Q-001 | verification | inspection | inspect `/settings/digest` at fictional commit `abc1234` against Q-001 | Active weekday and next delivery are visible to the reviewer. | Confirmed by the authorised product reviewer. | `evidence/digest-preference-review.md#q-001` |

### Evidence limits

- The focused checks did not evaluate unrelated digest scheduling behaviour.
- The repository's full regression and release process still applies.
- The inspection supports the stated content requirement and does not establish broader usability.

## Result

- **Supported claims:** R-001, R-002, R-003, Q-001
- **Unresolved claims:** none within this change
- **Required next action:** run the repository's existing release process
