# Isolated Bugsink 2.6.3 gate

This lane boots a disposable Bugsink 2.6.3 instance for every run. It does not reuse, stop, reconfigure or mutate the existing local Bugsink service on port 8100.

## What it proves

`bun run test:bugsink`:

1. creates fresh lab-owned state with two SQLite databases;
2. starts Bugsink on random loopback ports;
3. creates a synthetic project and project-bound read token;
4. sends one fixed canary error from a fresh Chromium context;
5. reads the issue and event back through Bugsink's canonical API;
6. compares the complete stored payload with the sent payload;
7. proves visible application recovery after the canary;
8. scans generated Bugsink evidence for runtime secrets;
9. closes the browser, server and child process;
10. removes the temporary state and proves the ports can bind again.

The browser receives the public ingestion key, which is expected. It does not receive the read token, runtime-file path or temporary state location.

## Data boundary

The canary payload is deliberately small and recognisable. Arbitrary error messages, stacks, URLs, cookies, request bodies, user fields and breadcrumbs are not captured. Unexpected errors are reduced to a fixed redacted value.

Phone-home traffic, webhook delivery and email are disabled. All generated state belongs to the run and is deleted in `finally`.

## Deliberate failures

The gate supports five named failure injections:

```bash
bun scripts/bugsink-gate.mjs failure-bootstrap --fail-bootstrap
bun scripts/bugsink-gate.mjs failure-callback --fail-callback
bun scripts/bugsink-gate.mjs failure-already-exited --fail-already-exited
bun scripts/bugsink-gate.mjs failure-output --fail-output
bun scripts/bugsink-gate.mjs failure-response --fail-response
```

Each command must exit 1, prove that the named failure point was reached, and still satisfy the cleanup contract.

## Local runtime requirement

The present lab checkout expects the isolated Bugsink virtual environment at the local path encoded in `scripts/bugsink-gate.mjs` and `scripts/candidate.mjs`. This is intentional for the current exact-candidate evidence, but it is not portable yet.

Before running this lane elsewhere, install Bugsink 2.6.3 in a dedicated virtual environment and update the runtime path in both files. Do not point it at an existing Bugsink installation containing real state.

## Complete stack

```bash
bun run test:stack
```

That runs the deterministic candidate, Playwright journeys, isolated Bugsink gate and exact dependency audit. It does not perform the independent hostile review required for final closure.
