# Release checklist

Tags show the minimum profile: `[Lean+]`, `[Standard+]`, or `[High Assurance]`. Mark an out-of-scope item `N/A: <reason>`.

## Candidate

- [ ] `[Lean+]` The commit or working-tree state under review is recorded.
- [ ] `[Standard+]` A commit identity includes a clean-working-tree check.
- [ ] `[Standard+]` A dirty candidate uses the base commit plus a relevant-file identity.
- [ ] `[High Assurance]` Source, tests, instructions, lockfiles, runtime, browser, and generated contracts have defined fingerprints.
- [ ] `[High Assurance]` Generated reports and evidence outputs sit outside the candidate input set.

## Project brief

- [ ] `[Lean+]` The Project Brief records the current purpose, stakeholders, scope, requirements, constraints, and acceptance links.
- [ ] `[Lean+]` Critical journeys cover the changed behaviour.
- [ ] `[Lean+]` Open questions have an owner.

## Deterministic checks

- [ ] `[Lean+]` Changed rules have unit coverage.
- [ ] `[Lean+]` Changed boundaries have integration or contract coverage.
- [ ] `[Lean+]` One representative UI journey passes in a real browser when the product has a UI.
- [ ] `[Standard+]` Critical UI journeys pass in a real browser when the product has a UI.
- [ ] `[Lean+]` Permissions, persistence, reload, provenance, and cleanup pass where relevant.
- [ ] `[Lean+]` Exact commands and counts are recorded.

## Failure and recovery

- [ ] `[Standard+]` Relevant failure cases stop at the expected boundary.
- [ ] `[Standard+]` User-visible recovery matches the promise.
- [ ] `[Standard+]` Entered or accepted work survives as specified.
- [ ] `[Standard+]` Cleanup leaves the environment reusable.

## Model review

This section applies when the acceptance contract names a question that requires model review.

- [ ] `[Standard+]` The brief contains bounded questions about visible clarity or friction.
- [ ] `[Standard+]` The result follows the required schema.
- [ ] `[Standard+]` Required product journeys receive GREEN.
- [ ] `[Standard+]` The isolated negative control receives its expected RED.
- [ ] `[Standard+]` Deterministic evidence controls acceptance.

## Supply chain

- [ ] `[Lean+]` Direct dependencies follow project pinning policy.
- [ ] `[Lean+]` The lockfile change is reviewed.
- [ ] `[Lean+]` New packages satisfy the quarantine policy where the ecosystem supports it.
- [ ] `[Lean+]` The native audit command passes or every exception is documented.
- [ ] `[Standard+]` The dependency decision records the gap, reachability, fixed version, and rollback.

## Evidence

- [ ] `[Lean+]` The handoff records commands and exact results.
- [ ] `[Standard+]` Reports belong to the current candidate.
- [ ] `[Standard+]` Required reports exist and parse strictly.
- [ ] `[Standard+]` Failed attempts remain preserved.
- [ ] `[Standard+]` For the same candidate and check, the latest completed attempt controls closure.
- [ ] `[High Assurance]` Evidence hashes reconcile.
- [ ] `[High Assurance]` Malformed, missing, stale, mixed, and substituted evidence cases fail closed.

## Observability

This section applies when the product emits operational errors or events.

- [ ] `[Standard+]` A relevant recovery path is exercised in isolation.
- [ ] `[High Assurance]` A synthetic canary reaches the isolated tracker or project.
- [ ] `[High Assurance]` Sensitive fields stay outside the captured event.
- [ ] `[High Assurance]` Cleanup leaves no shared-service mutation.

## Independent review

- [ ] `[Standard+]` The reviewer is fresh and read-only.
- [ ] `[Standard+]` The brief asks for counterexamples and acceptance bypasses.
- [ ] `[Standard+]` Findings identify evidence and required repairs.
- [ ] `[Standard+]` Release blockers are resolved or accepted by the authorised owner.
- [ ] `[High Assurance]` The reviewer challenges candidate identity, parsers, report reconciliation, and forced failures.

## Handoff

- [ ] `[Lean+]` Outcome is stated plainly.
- [ ] `[Lean+]` Changed files are listed.
- [ ] `[Lean+]` Commands or procedures and exact results are listed.
- [ ] `[Lean+]` Evidence paths are listed.
- [ ] `[Lean+]` Remaining risks name an owner.
- [ ] `[Lean+]` One next action is clear.
