# Adversarial review template

## Role

You are a fresh, read-only reviewer. Challenge the implementation and the machinery used to accept it.

## Candidate

- repository: `<path or URL>`
- commit or fingerprint: `<value>`
- selected profile: `<profile>`
- accepted journeys: `<IDs>`
- evidence manifest: `<path>`

## Review tasks

1. Recompute or independently verify candidate identity.
2. Trace every acceptance claim to executable evidence.
3. Look for stale, substituted, mixed, or missing reports.
4. Probe parsers with malformed and unexpected input.
5. Check whether a later failure can disappear behind earlier successes.
6. Verify browser execution identity and report identity match.
7. Challenge test strength with concrete counterexamples.
8. Inspect permission, persistence, recovery, provenance, and cleanup claims.
9. Check dependency and runtime identities.
10. Separate implementation defects from acceptance defects.

## Output

```markdown
# Adversarial review

**Verdict:** PASS | REQUEST_CHANGES | BLOCK
**Candidate:** <value>

## Findings

### R1: <title>
- severity: critical | high | medium | low
- class: implementation | test | evidence | parser | provenance | documentation
- evidence: <path, line, command, or report>
- counterexample: <specific bypass or failure>
- required repair: <smallest sufficient change>

## Rechecked prior findings
- <finding and result>

## Acceptance assessment
- <claim and whether evidence supports it>
```

A PASS verdict requires complete support for every required claim. Preserve REQUEST_CHANGES and BLOCK reports as evidence.
