# Locked community research decisions

Date: 2026-11-08

This directory preserves both complete community-research runs, including prompts, structured reports, source ledgers, raw JSONL event streams, final worker messages and stderr. `RESEARCH_MANIFEST.json` binds the preserved bytes. `test/community-research.test.mjs` verifies the hashes, source references, provenance wording and the machine-readable decisions in `STACK_DECISIONS.json`.

## Controlling rule

**Less** means fewer dependencies, concepts, files, execution paths, contract authorities and LLM correction turns. It does not mean deleting owning deterministic checks, forcing server HTML onto rich client state, or adding every tool that received favourable practitioner comments.

Community reports are practitioner evidence and official capability evidence. They are not population consensus and do not admit dependencies. Local lab execution remains the authority for this lab.

## Retain

- Bun 1.4.4 as the only JavaScript runtime.
- Playwright Test as deterministic browser authority.
- The existing unit, HTTP/integration, contract, persistence, cleanup and provenance checks.
- Isolated Bugsink 2.6.3 injected-event/readback acceptance as the single error destination.
- Exact pins, reviewed lockfile hashes, seven-day release-age quarantine and one advisory triage queue.
- Hono for City Food Atlas and other working Hono applications. No framework migration is justified.
- Preact and MapLibre where existing rich interaction state warrants them.

## Constrain

- Midscene remains optional and bounded to visible UX judgment. `UNCLEAR` cannot pass and a Midscene result cannot overrule deterministic failure.
- Use one interactive browser-control interface only when it closes a measured investigation gap. Do not routinely pay for CLI, MCP and Midscene over the same flow.
- Trial Hono RPC only where a typed JSON consumer exists and the slice deletes duplicated DTO or fetch-wrapper code. Split large inferred route graphs when measured tooling cost warrants it.
- Prefer server-rendered HTML, optionally HTMX, for new server-owned forms/lists/content flows only when it removes more machinery than it adds. Use Preact islands for substantial local state. This is a design pattern, not an Atlas migration order.
- Add property/schema exploration or selective mutation testing only where escaped defects justify the extra runtime. Preserve minimized failures as fixed regressions.

## Not admitted

Playwright CLI, Playwright MCP, Hurl, Schemathesis, Pact, an Elysia/Eden migration, Sentry beside Bugsink, and additional overlapping advisory scanners are not lab dependencies. Each needs a demonstrated gap, measured net simplification, exact-version review and separate implementation authority.

## Remove duplication

- one routine browser-control interface;
- one owner for each HTTP scenario;
- one error destination;
- one primary advisory queue;
- one contract authority per application boundary.

## Deterministic order

1. Typecheck, compile and focused lint.
2. Unit, regression, contract, property and integration checks.
3. Deterministic Playwright journeys.
4. Candidate hash, cleanup and provenance checks.
5. Bugsink injected-event readback.
6. Bounded LLM review only for residual visible judgment.

For consequential bug fixes, require a regression that fails on the old behaviour for the expected reason and passes after correction. Review acceptance cases before trusting implementation-generated expectations. The point is evidence, not TDD theatre.

## Security

Use exact pins, lockfile hashes, frozen installs, seven-day quarantine, one advisory queue, targeted reachability/capability review and periodic released-inventory refresh. Block known malware, unapproved integrity/source changes, credible reachable severe runtime/build vulnerabilities, unresolved new high-risk capability, and missing or stale required scans.

Do not repeat the same unchanged scan after every source edit. Do not use forceful automatic audit fixes or broad upgrades merely to erase a count. A documented unreachable finding needs an owner, rationale and expiry.

## LLM productivity claim

The research does **not** prove that Hono, Elysia, HTMX, Preact, Playwright CLI, MCP or Midscene universally improves LLM productivity. The working hypothesis is narrower: less helps when it lowers total concepts and correction surface without hiding required state, lifecycle or contract behaviour.

Future comparisons must hold model, prompt, task, time budget and deterministic acceptance tests constant. Measure successful-task tool turns, repair turns, escaped contract mistakes, dependencies introduced, files/concepts touched, deterministic failures, completed-task latency and billed usage.

## Preserved evidence

- Application-stack report: `application/COMMUNITY_STACK_REPORT.md`
- Application structured findings: `application/COMMUNITY_STACK_REPORT.json`
- Application source ledger: `application/SOURCES.json`
- Testing/security report: `testing/COMMUNITY_TESTING_REPORT.md`
- Testing/security structured findings: `testing/COMMUNITY_TESTING_REPORT.json`
- Testing/security source ledger: `testing/SOURCES.json`
- Machine contract: `STACK_DECISIONS.json`
- Hash manifest: `RESEARCH_MANIFEST.json`
