# Astra-high adversarial repair record

**Review verdict:** `REQUEST_CHANGES`  
**Review artifact:** `ADVERSARIAL_REVIEW.md`  
**Disposition:** all eight blocking findings repaired; fresh exact-candidate acceptance still required

The prior mechanically passing gate7 result was rejected as final acceptance. The hostile review found eight gaps that ordinary GREEN tests had missed.

## Focused RED/GREEN chronology

### Initial hostile-regression RED

Command:

```text
bun test test/acceptance-contract.test.mjs
```

Observed before repair:

- 1 passed;
- 5 failed;
- Bun contradictory summary rejection failed;
- recursive Playwright step-error rejection failed;
- browser report provenance binding failed;
- audit stderr rejection failed;
- separate audit artifact expectations failed.

The candidate-runtime test separately failed because `candidatePaths` did not contain the selected `chromium_headless_shell-1243` tree.

The overlap tests separately failed at the new server-side barrier because the server did not yet expose the body-read boundary. The failure was bounded by a 500 ms deterministic timeout rather than an unbounded wait.

### Focused GREEN

Command:

```text
bun test test/acceptance-contract.test.mjs test/closure.test.mjs test/api.test.mjs
```

Observed after the first repair set: **16 passed, 0 failed**.

A second focused RED/GREEN cycle covered Playwright list-log reconciliation. The permissive placeholder accepted a stale journey title; after repair the acceptance-contract file passed **6/6**.

The complete deterministic suite then passed **53/53 across 15 files**.

## Finding dispositions

### ADV-01: actual browser runtime omitted

- Added the revision-matched `chromium_headless_shell-1243` tree to candidate identity.
- Kept the regular Chromium application bound as well.
- Added a deterministic candidate-path regression.

### ADV-02: browser evidence replay

- Recorder injects the execution UUID and candidate ID into Playwright metadata.
- Playwright reports must carry those exact values.
- Report start/duration must fall inside the recorded execution interval.
- Browser list logs must contain the exact accepted titles and passing count.
- Midscene review JSON carries the same execution and candidate bindings.
- Recorder and closure use the same binding, report and log helpers.

This protects against stale or accidentally substituted reports inside the lab's trusted local recorder boundary. It is not a cryptographic defence against an attacker who can rewrite the candidate, recorder and all evidence.

### ADV-03: creator versus completion requester

The governing rule is now explicit: the person requesting completion cannot approve their own request. The original creator may approve when a different person requested completion.

The API regression now proves both sides while the delayed request is parked:

- Sam requests completion and cannot self-approve;
- Alex, the original creator but not the completion requester, may approve.

### ADV-04: overlap was timing-dependent

- Added an optional server instrumentation hook immediately before mutation-body consumption.
- Tests arm a barrier only after setup.
- The barrier acknowledges that every target handler is parked before request bodies are released or another mutation overtakes it.
- The stale task snapshot is still read only after body consumption.

The hook is inert in ordinary runtime use.

### ADV-05: Bun parser ambiguity

The parser now rejects:

- positive skip or todo summaries;
- malformed result-looking lines;
- invalid timing suffixes;
- ANSI and other disallowed controls;
- duplicate or malformed accepted identities;
- path traversal in accepted test paths;
- malformed final summary syntax.

### ADV-06: nested Playwright errors

`reportPassed` now recursively rejects errors in nested Playwright step trees as well as result-level singular and plural errors.

### ADV-07: audit stream provenance

- Recorder preserves UUID-bound merged, stdout and stderr logs separately.
- Audit acceptance receives exit, stdout and stderr independently.
- Any stderr fails, including JSON emitted only on stderr.
- Canonical audit JSON remains a separately hash-bound artifact.
- The ordinary stack audit, recorder and closure now use the same pure audit helper.

### ADV-08: mismatched research titles and claims

The reconciled research now correctly identifies:

- arXiv `2602.11988v3` as the AGENTS.md repository-context study;
- arXiv `2610.38214` as Skeleton-Guided Program Synthesis.

Claims were narrowed to what those papers support. The preserved Astra report is explicitly labelled raw analysis rather than governing authority.

## Residual limits

- Local evidence is integrity-checked within a trusted recorder boundary, not cryptographically signed against a hostile local administrator.
- Before/after snapshots cannot detect a candidate mutation that is changed and perfectly restored entirely between snapshots.
- Cross-process and distributed concurrency remain deferred until the lab admits multiple writers.
- Fresh exact-candidate acceptance and another independent hostile review remain mandatory before final closure.
