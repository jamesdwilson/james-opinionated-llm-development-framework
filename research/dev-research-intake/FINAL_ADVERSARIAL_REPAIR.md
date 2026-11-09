# Final Astra-high verifier repair record

**Review verdict:** `REQUEST_CHANGES`  
**Review artifact:** `FINAL_ADVERSARIAL_REVIEW.md`  
**Reviewed candidate:** `1460ddebf78200eea93bf053ce5aff8596092878f7bda909f73c0bb5d144f646`  
**Disposition:** four verifier defects repaired with deterministic regressions; fresh exact-candidate acceptance and a new independent hostile review remain required

The gate8 evidence was internally consistent, but Astra found four ways a future bad evidence set could still be accepted. The gate8 pass was therefore not promoted to final acceptance.

## RED first

Command:

```text
bun test test/acceptance-contract.test.mjs test/closure.test.mjs
```

Observed before repair: **11 passed, 4 failed**.

The four failures reproduced:

1. a later exact-candidate Bun failure being ignored after two earlier successes;
2. a browser result title with an accepted-title prefix being accepted;
3. control-prefixed or malformed Bun result-shaped output being ignored;
4. Playwright retry, result-time and malformed-step evidence being accepted.

## Repairs

### FR-01: unresolved later failures

The authoritative acceptance batch is every evidence record whose complete before and after manifests equal the candidate under review. Every record in that batch must independently verify and have its required exit code. Named failure injections remain valid only when their expected exit is 1 and their cleanup semantics verify. Additional failed Bun, Chromium, Bugsink, review or audit records now block closure instead of being filtered out.

Regression: `F4 closure rejects an unresolved later exact-candidate gate failure`.

### FR-02: browser log title ambiguity

The Playwright list log is now parsed with one complete pinned line grammar. The verifier extracts marker, ordinal, exact source file, source line, source column, exact title and duration. It compares exact titles rather than substring prefixes and requires the expected spec file.

Regression: `browser log acceptance rejects prefix, hierarchy and source ambiguity`.

### FR-03: Bun result-shaped ambiguity

The Bun verifier now rejects every control character except newline in the captured payload, including carriage returns and tabs. Any line that looks like a result or pass/fail/skip/todo summary must match the complete accepted grammar; malformed or prefixed variants fail rather than being ignored.

Regression: `Bun acceptance rejects control-prefixed and malformed result-shaped output`.

### FR-04: incomplete Playwright result validation

The Playwright verifier now requires:

- a valid non-inverted execution interval;
- report timing fully inside that interval;
- exactly one passing result with `retry === 0`;
- finite non-negative result duration;
- result timing inside both the execution and report intervals;
- structurally valid nested step objects with non-empty titles, finite non-negative durations, no singular error and no malformed plural-errors field.

Regression: `Playwright acceptance rejects retries, stale result timing and malformed steps`.

## GREEN

The focused command then passed **15/15**. The complete deterministic suite passed **57/57 across 15 files**. `bun run test:stack` also exited 0, including six Chromium journeys, isolated Bugsink 2.6.3 and exact empty audit output.

## Remaining work

The repair changed candidate-bound code, tests, accepted-check authority and research records. The previous candidate and gate8 evidence are therefore historical. The new candidate still requires the complete repeated acceptance sequence and a fresh independent Astra-high hostile review before final closure.

The first complete acceptance attempt for the repaired verifier correctly failed closure. Its second Midscene review encountered a transient upstream 503, retried and produced the expected visible verdict, but Playwright retained the warning in the result's stderr evidence. The stricter verifier rejected both review records and, as intended, would not ignore them merely because another pair passed. This candidate is therefore historical rather than accepted; the transient-failure record is preserved, not relabelled or deleted.
