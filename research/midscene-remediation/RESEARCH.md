# Midscene remediation research

Date: 2026-11-08 CST / 2026-11-09 UTC

## Outcome

A slightly older Midscene release does not improve the dependency problem. `@midscene/web@1.12.5` resolves the same six vulnerable package names and the same 13 advisories as the pinned 1.17.4 graph: 10 high and 3 moderate.

A bounded Playwright-only remediation is viable for this lab:

- keep the already characterised `@midscene/web@1.17.4` API;
- replace unused `@midscene/playground` and `puppeteer-core` installations with local fail-closed packages;
- override the four packages required by the observation route to advisory-fixed, quarantine-eligible versions:
  - `js-yaml@4.3.2`;
  - `sharp@0.35.5`;
  - `uuid@11.1.1`;
  - `zod@4.6.6`;
- retain Playwright Test as the browser driver and deterministic authority.

The disposable spike produced an empty `bun audit --json` result and passed both real SIWC-backed review journeys:

- J05: `RED / stopped_at_unclear_choice`;
- J06: `GREEN / completed_goal`;
- Playwright: 2/2 passed;
- neither fail-closed stub was imported.

This is intentionally narrower than claiming all Midscene features work. Puppeteer, Playground, and any future route that imports either stub are unsupported and fail immediately. The proven contract is the lab's Playwright observation and structured visible-UX review route.

## Why not downgrade

Registry manifests for Midscene 1.12.5 through 1.17.7 retain the same relevant dependency constraints:

- `puppeteer-core@24.6.0`;
- `js-yaml@4.1.0`;
- `sharp@^0.34.3`;
- `uuid@11.1.0`;
- `zod@^3.25.1`.

The isolated 1.12.5 installation therefore reproduced the exact current advisory set rather than reducing it.

## Current upstream state

- Latest stable at research time: `1.17.7`, published 2026-11-06. It retains the vulnerable relevant constraints.
- Published beta: `1.17.8-beta-20261106101231.0`, published 2026-11-06. It moves to `js-yaml@4.3.2`, `sharp@^0.35.5`, and `uuid@11.1.1`, but retains `zod@^3.25.1` and `puppeteer-core@24.6.0`.
- The beta is not seven-day-quarantine eligible until 2026-11-13 UTC and is not audit-clean on its manifest alone.
- Upstream PR #3358 remains open and unmerged. It may be inspected but must not be executed or treated as released remediation.

Official sources:

- https://github.com/web-infra-dev/midscene/releases/tag/v1.17.7
- https://github.com/web-infra-dev/midscene/pull/3356
- https://github.com/web-infra-dev/midscene/pull/3358
- https://registry.npmjs.org/@midscene/web
- https://registry.npmjs.org/@midscene/core
- https://registry.npmjs.org/@midscene/shared
- https://registry.npmjs.org/@midscene/playground

## Disposable spike evidence

Location: `/Users/james/.hermes-next-v0.22.4/cache/scratch/midscene-remediation-spikes`

### Older release

- version: `@midscene/web@1.12.5`
- audit: 13 advisories across `basic-ftp`, `extract-zip`, `js-yaml`, `sharp`, `uuid`, and `zod`
- audit SHA-256: `4d115ab1949d64d7443a25d3a4111ca529088d6184f99f6220bd70f979d6bf04`

### Remediated 1.17.4 route

- package.json SHA-256: `276a9d23b6fae57ab249899a57d82b12341a26bfbc3a4e0554e5480fa7b5ddcb`
- bun.lock SHA-256: `0ba9a55a35f812c4df4f7bc2255dfe4822f18613cca061d5989e719ac9f70b6e`
- audit JSON SHA-256: `ca3d163bab055381827226140568f3bef7eaac187cebd76878e0b63e9e442356`
- J05 evidence SHA-256: `6542439984696a096bc044910a0b0245dc7b37e0d0baad29f09bf9cd2c5adaa5`
- J06 evidence SHA-256: `59dfb05a83e33e9e8d8eda8a24584593195ccb5ab5a1839b3cf5ee52b4fabd98`

## Acceptance boundary

The spike establishes feasibility only. Lab acceptance requires the complete exact-candidate deterministic, Chromium, isolated Bugsink, injected-cleanup, repeated Midscene, audit, scan, and closure sequence. A Midscene result remains unable to override deterministic evidence.

## Hostile-review correction

An independent adversarial review accepted the dependency reduction and real Playwright evidence but rejected the first closure result because the closure gate trusted stored verification flags, allowed repeated evidence to be satisfied by relabeling, and left the canonical stack command wired to the obsolete audit blocker.

The gate was corrected before final acceptance:

- exact commands and artifact paths are bound to each execution kind;
- artifact contents are independently parsed by the closure gate;
- before/after manifests must exactly equal the current candidate, including failure records;
- repeated runs require distinct execution identities, not merely distinct labels;
- the canonical stack audit command now executes a fresh current-graph audit and admits only an empty result.

All evidence recorded before those gate corrections became stale by candidate identity and must not satisfy the final closure.

A second adversarial review found that timestamps, artifact ordering and summary booleans were still too weak. The final gate therefore also requires:

- a random execution UUID written into both the execution record and the first line of its bound log;
- positive Bun pass counts, not merely zero failures;
- nonempty Playwright suites with no report errors as well as exact aggregate counts;
- complete Bugsink success fields and internally consistent scan counts;
- an explicit `failureMode` and `failureReached: true` marker for every injected failure, including a disposable marker written inside the isolated service before bootstrap/output injection;
- an audit value that is exactly a plain empty JSON object, not an empty array, false value or unexpected object shape.

The five injected failure modes were then exercised directly and each proved its named injection was reached with clean bounded scan evidence.

A third adversarial pass rejected remaining reliance on aggregate summaries. The closure verifier now recursively validates the exact expected Playwright journey titles, specs, tests and individual results; requires one authoritative positive Bun summary whose executed-test count matches its pass count; requires scan count and inventory consistency plus coverage of the run result; and reconciles the logged Bugsink result, stored result, cleanup identity and scan state. These checks reject internally contradictory evidence even when its top-level success fields remain green.

A fourth adversarial pass found two narrow contradictory shapes: a passing Playwright result with a populated singular `error`, and impossible negative or zero-byte scan counts. The verifier now rejects either shape, requires empty result `stderr`, preserves legitimate Midscene report notices in `stdout`, and requires scan bytes to cover at least the recorded run-result artifact while member and decoded counts remain nonnegative.
