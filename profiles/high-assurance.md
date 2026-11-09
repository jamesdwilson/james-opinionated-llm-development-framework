# High Assurance profile

## Best fit

- security or privacy boundary;
- financial or legal consequence;
- difficult rollback;
- critical data integrity;
- high operational cost of failure;
- acceptance machinery with several parsers, runners, or generated reports.

## Required artefacts

Everything in Standard, plus:

- exact candidate fingerprint definition;
- accepted-check inventory;
- hashed evidence manifest;
- closure verifier;
- forced-failure catalogue;
- isolated observability plan where the product emits operational errors or events;
- hostile read-only review brief.

## Required checks

- repeated clean deterministic runs;
- repeated critical browser journeys;
- malformed, missing, stale, mixed, and substituted evidence cases;
- forced bootstrap, callback, timeout, child-process, output, and cleanup failures where relevant;
- exact dependency and runtime identity;
- isolated error-capture canary using synthetic data where observability is in scope;
- fail-closed parsing and closure;
- hostile review of both implementation and acceptance machinery.

## Evidence rules

- Hash source inputs, lockfiles, runtime identity, browser identity, reports, and manifests.
- Record stdout and stderr separately.
- Preserve failed attempts.
- Treat a later failure as controlling evidence.
- Reject ambiguous or unrecognised fields in acceptance summaries.
- Recompute the candidate after every relevant change.

## Closure

A High Assurance change closes when the exact candidate completes the accepted inventory, evidence hashes reconcile, forced failures fail at the expected boundary, cleanup succeeds, and hostile review returns a clean verdict.
