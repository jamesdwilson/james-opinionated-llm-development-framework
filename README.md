# James's Opinionated LLM Development Framework

> Let the model write code. Never let it mark its own homework.

This repository is an executable research lab for one expensive question: **how do we let LLMs move quickly without letting a convincing pile of green text pass as proof?**

The short answer is deterministic tests, exact candidate identity, hostile review, small tools with narrow jobs, and an almost unreasonable suspicion of cheerful summaries.

The lab uses a tiny household-task application as its specimen. The app is deliberately boring. The testing problem is not.

## Status

This is a working research framework, not a finished standard and not a magic prompt collection.

The current acceptance contract requires:

- 57 deterministic checks across 15 files;
- six Playwright browser journeys;
- two isolated Bugsink runs;
- five deliberate failure injections;
- two clean pairs of bounded Midscene reviews;
- an exact empty dependency audit;
- candidate and evidence hash reconciliation;
- an independent adversarial review after the machinery says everything passed.

A green command is evidence. It is not absolution.

## The opinionated bits

### 1. Start with the promise

The North Star, journey catalogue and acceptance inventory are versioned beside the code. They define what the product promises before an agent starts inventing architecture.

Repository guidance can help agents, but more context is not automatically better. A 2026 study of `AGENTS.md` files found that generated context could raise inference cost and, in some settings, reduce task success.[12] We keep instructions short, executable where possible, and tied to real decisions.

### 2. Tests before implementation claims

The framework follows RED, GREEN, then repair. A claimed fix needs a failing counterexample first unless the work is explicitly characterised as documentation-only.

Recent research on full-stack agent development uses iterative test generation, implementation and repair rather than treating one successful generation as delivery.[13] TestSuiteBench reaches the less flattering conclusion: strong repository-level test suites remain difficult for coding agents to produce from specifications.[14] That is why the accepted test inventory is itself reviewed and hashed.

### 3. Deterministic systems outrank model judgement

Bun owns the fast unit, API, persistence, policy and verifier checks. Its test runner is built into the runtime and supports familiar Jest-style primitives.[3]

Playwright owns browser mechanics: visible behaviour, permissions, reloads, state, responsive layouts, provenance and cleanup. Its own guidance recommends testing user-visible behaviour and keeping tests isolated.[1]

Midscene is the mystery shopper, not the judge. It extends Playwright with AI-assisted page understanding and actions,[6] but here it only reviews bounded visible UX questions. It cannot overrule a failing API, persistence, permission, audit or Playwright check.

### 4. One tool, one job

- **Bun** runs JavaScript and the deterministic test suite.
- **Playwright** proves browser behaviour.
- **Midscene** judges limited visible friction where exact assertions are a poor fit.
- **Bugsink** captures one deliberately bounded canary error and proves that recovery still works. Bugsink is a self-hosted error tracker built around the Sentry SDK protocol.[7]
- **SQLite** gives the sample application real persistence without adding a service zoo.
- **Astra-high** performs read-only hostile review after the ordinary stack passes.
- **The closure verifier** checks the evidence rather than trusting filenames, exit codes or somebody saying "looks good".

Playwright also publishes planner, generator and healer agents.[2] We treat those as upstream assistance, not acceptance authority. Letting an agent write both the exam and the answer key is efficient in the same way removing the brakes makes a car lighter.

### 5. The exact bytes matter

Each acceptance run records a candidate fingerprint over the code, tests, policy documents, lockfiles, installed packages, the selected Playwright browser runtime and the isolated Bugsink runtime.

A run passes only if:

- the candidate is unchanged before and after execution;
- the report names the exact accepted tests;
- every recorded artefact still matches its hash;
- browser reports carry the correct execution ID, candidate ID and time interval;
- stdout and stderr remain separately provable;
- a later failure cannot be ignored because two earlier runs happened to pass.

This is local integrity checking, not a cryptographic defence against an administrator who controls the whole machine. It is meant to catch stale evidence, accidental substitutions, permissive parsers and convenient storytelling.

### 6. Failure is a first-class test case

The Bugsink lane deliberately injects failures during bootstrap, callbacks, child-process exit, bounded output and oversized responses. Every case must fail in the expected place and still prove cleanup.

Concurrency tests park requests at a server-side barrier before allowing them to proceed. That proves the intended overlap instead of hoping two promises happen to interleave. Research on agents sharing a codebase likewise treats coordination and interference as real system properties rather than clerical details.[15]

### 7. Observability must not become data hoarding

The canary error has a fixed shape. Arbitrary messages, cookies, request bodies, user fields and credentials are not collected. The isolated Bugsink instance uses synthetic state, random loopback ports, fresh databases and complete cleanup.

The existing local Bugsink service is observed but never reused or mutated by the lab. Production-ish systems make dreadful test fixtures.

### 8. Supply-chain security should be boring

Dependencies are pinned. Lockfiles are hashed. Bun's package manager can delay newly published packages with `minimumReleaseAge`, which gives the ecosystem time to discover a bad release before it enters the graph.[4] `bun audit` checks the resolved dependency tree against vulnerability data.[5]

The framework does not churn the lockfile because a newer version exists. It does not run broad automatic "fix everything" commands. It asks whether the vulnerable code is reachable, whether a fixed version exists and whether the upgrade removes more risk than it introduces.

### 9. Independent review comes after green

The final reviewer is read-only and receives an explicit hostile brief. It must re-check prior findings, search for new bypasses, recompute the candidate identity and inspect the evidence chain.

This is not theatre. The hostile reviews in this lab invalidated more than one mechanically green run. They found stale-report replay, parser ambiguity, incomplete browser provenance, mixed audit streams, timing-dependent concurrency tests and a closure rule that could ignore a later failed run.

Long-running agent work benefits from durable progress records, explicit tests and incremental handoffs.[8] OpenAI's harness work makes a similar point from another angle: repository legibility, enforceable invariants and fast feedback loops matter more as agents do more of the implementation.[9]

### 10. Less is a technical requirement

Every dependency, model call, parser and abstraction has to earn rent.

Martin Fowler's harness analysis is useful here: infrastructure is worth carrying when it turns real uncertainty into repeatable signal, not because "agent harness" looks good in a diagram.[10] METR's updated field study is another useful cold shower. Tooling that feels faster does not automatically produce a measured productivity gain in real repositories.[11]

The framework therefore prefers:

- one runtime;
- one deterministic browser authority;
- one accepted journey catalogue;
- one small application with real persistence;
- pure verification helpers shared by recording and closure;
- native semantics and stable names instead of locator acrobatics;
- no abstraction before a second real use exists.

## The loop

```text
research and product promise
        ↓
versioned North Star + journeys + exact accepted checks
        ↓
RED test or explicit characterisation
        ↓
small implementation change
        ↓
Bun deterministic suite
        ↓
Playwright browser journeys
        ↓
isolated Bugsink + forced failures + cleanup
        ↓
exact dependency audit
        ↓
bounded Midscene visible-UX reviews
        ↓
candidate/evidence closure
        ↓
independent hostile review
        ↓
PASS, or new counterexample → repair → run the whole thing again
```

Yes, running it again is tedious. So is debugging a false release with a toddler asking what the laptop is doing.

## Evidence hierarchy

When signals disagree, the order is deliberate:

1. security and permission failures;
2. deterministic domain, persistence and API checks;
3. deterministic Playwright journeys;
4. isolated failure and recovery evidence;
5. dependency audit;
6. bounded Midscene UX judgement;
7. prose summaries.

A Midscene GREEN cannot rescue a deterministic RED. A polished report cannot rescue missing bytes. `UNCLEAR` cannot pass.

## The two model-reviewed journeys

- **J05 is the negative control.** The interface intentionally presents an unexplained required choice. The expected verdict is `RED / stopped_at_unclear_choice`.
- **J06 is the corrected journey.** The interface explains the approval choice, shows who must act next, supports recovery and finishes with visible provenance. The expected verdict is `GREEN / completed_goal`.

If the reviewer starts calling both versions good, the reviewer has stopped being useful.

## Repository map

- `NORTH_STAR.md` - the product promise and authority rules.
- `JOURNEY_CATALOG.md` - accepted behavioural journeys.
- `ACCEPTED_CHECKS.json` - exact deterministic and browser test inventory.
- `ACCEPTANCE_MATRIX.md` - what each layer proves and what it does not.
- `LLM_POLICY.md` / `llm-policy.json` - model roles and reasoning limits.
- `src/` - the small task application and SQLite-backed server.
- `public/` - the deliberately plain browser UI.
- `test/` - unit, API, persistence, policy, concurrency and verifier tests.
- `e2e/` - Playwright journeys and bounded Midscene review drivers.
- `scripts/` - candidate hashing, evidence recording, Bugsink isolation, auditing and closure.
- `research/` - source ledgers, community research and adversarial review records.
- `stubs/` - fail-closed replacements for powerful transitive packages the accepted path does not use.

Program structure itself can serve as a useful specification for coding agents,[16] so this map is intentionally dull and literal. Dull code is easier for humans, models and future you to inspect.

## Running the portable parts

The repository currently pins Bun 1.4.4.

```bash
bun install --frozen-lockfile
bun x --bun playwright install chromium
bun run test:deterministic
bun run test:browser
bun scripts/audit-block.mjs
```

The full Bugsink and exact-candidate closure lanes currently expect an isolated Bugsink 2.6.3 virtual environment and the lab's local runtime configuration. See `scripts/bugsink/README.md` before attempting the complete stack.

```bash
bun run test:stack
bun run test:reviews
bun run test:closure
```

Do not treat `test:stack` as final acceptance by itself. Independent hostile review remains deliberately outside the self-certifying batch.

## What this framework does not claim

- It does not prove that an LLM-generated implementation is generally correct.
- It does not replace human product judgement.
- It does not solve distributed concurrency before the system has multiple writers.
- It does not make probabilistic UX review deterministic by pretending harder.
- It does not authenticate evidence against a hostile machine owner.
- It does not justify every tool in every repository.

It does give the model fewer places to bluff, which is a decent start.

## Research posture

The papers and vendor guidance inform the framework. They do not get to smuggle dependencies into it.

A proposal is admitted only when it closes a demonstrated gap, removes more complexity than it adds, has a narrow owner and survives the same acceptance machinery as the rest of the candidate. The research ledger for this README lives at `research/framework-readme-citation-ledger.json`.

## Sources

[1] https://playwright.dev/docs/best-practices - Playwright best practices
[2] https://playwright.dev/docs/test-agents - Playwright Test Agents
[3] https://bun.com/docs/test - Bun test runner
[4] https://bun.com/docs/runtime/bunfig - Bun configuration
[5] https://bun.com/docs/pm/cli/audit - Bun audit
[6] https://midscenejs.com/integrate-with-playwright.html - Midscene.js Playwright integration
[7] https://www.bugsink.com/docs - Bugsink documentation
[8] https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents - Effective harnesses for long-running agents
[9] https://openai.com/index/harness-engineering - Harness engineering
[10] https://martinfowler.com/articles/are-harnesses-worth-the-cost.html - Are harnesses worth the cost?
[11] https://metr.org/blog/2026-02-24-uplift-update - Measuring the Impact of Early-2025 AI on Experienced Open-Source Developer Productivity
[12] https://arxiv.org/abs/2602.11988 - Evaluating AGENTS.md: Are Repository-Level Context Files Helpful for Coding Agents?
[13] https://arxiv.org/abs/2605.17242 - From Runnable to Shippable: Multi-Agent Test-Driven Development for Generating Full-Stack Web Applications from Requirements
[14] https://arxiv.org/abs/2610.13065 - TestSuiteBench: Coding Agents Struggle to Generate Strong Test Suites from Specifications
[15] https://arxiv.org/abs/2611.00314 - Decentralized Multi-Agent Coordination and Communication in Shared Codebases
[16] https://arxiv.org/abs/2610.38214 - Skeleton Coding: Program Structure as a Specification for Agents
