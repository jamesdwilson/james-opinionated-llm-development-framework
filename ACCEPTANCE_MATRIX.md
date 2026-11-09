# Acceptance matrix

## Deterministic owner layers

- Domain unit/model tests: task states, approval policy, actor constraints and idempotency.
- SQLite persistence integration: reopen durability and ordered event lineage.
- HTTP contract tests: validation, status codes, response schemas and permission failures.
- Playwright: accessible interaction, keyboard path, responsive composition, reload, permissions, provenance and cleanup.

## Probabilistic layer

- Midscene cold-user negative control: J05.
- Midscene corrected whole-journey review: J06.
- Midscene verdicts are local model-bound evidence, never release authority.

## Candidate closure

The candidate is acceptable only if all deterministic tests pass, J05 returns RED for the ambiguous control, J06 returns GREEN for the corrected flow, neither review returns UNCLEAR, repeated exact runs agree materially, and dependency/capture limits are recorded.

The authoritative acceptance batch is every evidence record whose complete before and after manifests equal the candidate being reviewed. Every record in that batch must independently verify and return its required exit code. A later failed Bun, Chromium, Bugsink, review or audit execution cannot be ignored because earlier successes already met the minimum count. Named failure injections are the only expected nonzero exits; each must exit 1, reach its declared failure mode and prove cleanup.

J06 requires completed_goal and empty visible contradictions. Midscene does not prove or need to recognize a document reload or backend persistence. Truthful unvisitedScope limitations are expected; deterministic Playwright owns reload on the same unchanged candidate.
