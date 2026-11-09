# Evidence record template

## Run

- **Run ID:** `<stable identifier>`
- **Candidate:** `<verified clean commit or working-tree fingerprint>`
- **Profile:** Lean | Standard | High Assurance
- **Started:** `<timestamp with timezone>`
- **Finished:** `<timestamp with timezone>`

## Environment

- operating system: `<value>`
- runtime: `<name and version>`
- package manager: `<name and version>`
- browser: `<name, version, and path or package identity>`
- material services: `<name and version>`

## Checks

| Check ID | Requirement IDs | Method | Procedure or command | Result | Evidence | Hash |
|---|---|---|---|---|---|---|
| C01 | `<R-001, Q-001>` | test | `<command>` | `<exit and counts>` | `<report path>` | `<hash when required>` |
| V01 | `<Q-002>` | inspection | `<review procedure>` | `<recorded observation>` | `<report path>` | `<hash when required>` |

## Candidate integrity

- identity before checks: `<value>`
- identity after checks: `<value>`
- changed during run: yes | no
- identity method: clean commit | canonical relevant-tree fingerprint
- dirty-tree coverage: additions, modifications, deletions, types, modes, and symlink targets
- excluded generated paths: `<reports, evidence outputs, caches>`

## Failures

- `<failed attempt, expected failure, or none>`

## Review

- reviewer: `<fresh reviewer identity>`
- brief: `<path>`
- verdict: PASS | REQUEST_CHANGES | BLOCK
- findings: `<path>`

## Closure

- **Verdict:** PASS | FAIL | BLOCKED
- **Reason:** `<one precise sentence>`
- **Remaining risk:** `<risk and owner>`
- **Next action:** `<one concrete action>`
