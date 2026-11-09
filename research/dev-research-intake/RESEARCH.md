# Dev Research Intake Reconciliation

**Status:** implemented and pending exact-candidate re-acceptance  
**Intake:** `INTAKE.md`  
**Analysis model:** `gpt-6-astra`, high reasoning, read-only sandbox  
**Analysis trace:** `ASTRA_HIGH_ANALYSIS.md`
**Adversarial review:** `ADVERSARIAL_REVIEW.md`  
**Repair record:** `ADVERSARIAL_REPAIR.md`  
**Final adversarial review:** `FINAL_ADVERSARIAL_REVIEW.md`  
**Final verifier repair:** `FINAL_ADVERSARIAL_REPAIR.md`

## Decision

The intake was useful as a map, not as implementation authority. The lab already had the expensive parts that the strongest current research asks for: deterministic acceptance, a controlled browser environment, stateful journeys, evidence capture, restart/recovery checks, model-role boundaries, and independent hostile review.

The accepted delta is deliberately small:

1. bind the accepted journey catalogue and exact deterministic check inventory into candidate identity;
2. make Bun acceptance prove the exact reviewed test names and source files, not merely a passing count;
3. prove two overlapping HTTP mutations cannot duplicate provenance or overwrite a later state;
4. make the server derive mutable state after request-body await points rather than using a stale pre-await snapshot;
5. make canonical audit JSON a first-class recorded artifact;
6. share pure Bun, Playwright and audit acceptance helpers between recording and closure so those two gates cannot drift.

No dependency was added.

## Adversarial correction

The first fresh mechanical acceptance run passed, but the independent Astra-high hostile review returned `REQUEST_CHANGES` with eight blocking findings. That mechanical pass was not promoted. The complete finding set and its repairs are preserved in `ADVERSARIAL_REVIEW.md` and `ADVERSARIAL_REPAIR.md`.

The repairs bind the actual headless browser runtime, bind browser and review artifacts to execution/candidate/time, force deterministic server-side overlap, tighten Bun and recursive Playwright parsing, preserve audit stdout/stderr separately, resolve the approval authority, and correct two mismatched research citations.

The next complete rerun also passed mechanically, but the second Astra-high hostile review found four remaining verifier bypasses: later failed runs could be ignored after enough successes, browser list logs used prefix matching, control-prefixed Bun output could be ignored, and Playwright retries/result times/malformed steps were not fully checked. Those four defects now have RED-first deterministic regressions and fail-closed repairs. The previous mechanical pass remains historical. Fresh exact-candidate acceptance and another independent hostile review remain required.

## Why these changes were admitted

The recent primary research supports executable acceptance and stronger repository context, but the results are narrower than the intake sometimes implies. The AGENTS.md study found modest performance changes and higher generated-context cost rather than a universal win; TDDev centres iterative acceptance-test-and-repair; TestSuiteBench evaluates real test-suite construction in containerised repositories; and Skeleton Coding studies whether explicit program structure improves code generation. [1][2][3][4]

ParallACT is especially relevant to the overlap regression: it treats concurrent actions as a source of interference and requires validation after actions, rather than assuming that individually sensible operations compose safely. [5] The lab does not need ParallACT as a dependency to adopt the demonstrated principle.

The harness literature also supports the lab's existing direction. Anthropic emphasises a stable environment, tests and persistent progress for long-running agents; OpenAI describes repository-local legibility, enforced invariants and feedback loops; Fowler argues that a harness must earn its carrying cost; and METR's updated field experiment is a useful warning that plausible tooling improvements do not automatically produce measured productivity gains. [12][13][14][15]

## Implemented changes

### 1. Candidate-bound authorities

- `JOURNEY_CATALOG.md` is now inside `candidatePaths`.
- `ACCEPTED_CHECKS.json` is now inside `candidatePaths`.
- `ACCEPTED_CHECKS.json` is the machine-readable authority for:
  - exact deterministic test file and title pairs;
  - exact Chromium journey titles;
  - exact bounded Midscene review titles.

This prevents a candidate from retaining the same identity while its accepted behaviour authority changes.

### 2. Exact deterministic acceptance

`scripts/acceptance-contract.mjs` now parses Bun's per-test result lines and compares the exact observed `(file, title)` set with `ACCEPTED_CHECKS.json`.

Acceptance rejects:

- a coherent but smaller passing suite;
- a substituted test with the same count;
- duplicated test identities;
- skipped, todo or failed checks;
- disagreement between detailed results and Bun's summary.

The closure gate and run recorder both use the same pure verifier.

### 3. Deterministic overlap regressions

Two API regressions use deliberately held request bodies rather than sleeps:

- two overlapping approvals produce exactly one `task.approved` event, with one idempotent response;
- a delayed stale completion cannot overwrite a later approved state.

The production correction is one line of behaviour: route matching still verifies that the task exists, but the mutable task snapshot is re-read after `await readJson(request)` and immediately before transition logic.

This is the smallest correction for the demonstrated single-process race. It does not pretend to solve cross-process or distributed concurrency.

The independent-approval rule is now explicit: the person requesting completion cannot approve their own request. The original creator may approve when a different household member requested completion. This matches the visible promise that another person approves the completion request and avoids silently conflating creator with completion requester.

### 4. Canonical audit evidence

Recorded audit runs now preserve both:

- the execution log with its UUID binding;
- a canonical `*-audit.json` payload.

Audit acceptance still requires exit zero and an exact plain empty JSON object `{}`. The new artifact makes the accepted payload independently hashable rather than forcing downstream tools to recover JSON from a mixed log.

### 5. Shared acceptance logic

The exact Bun inventory check, recursive Playwright result check, exact audit payload check and expected artifact mapping now live in `scripts/acceptance-contract.mjs`.

This is not a new abstraction layer. It removes duplicated acceptance rules from `record-run.mjs` and `closure-gate.mjs`, making the recording and closure decisions use the same small pure functions.

## Kept unchanged

- Bun 1.4.4 remains the only JavaScript runtime.
- Playwright remains deterministic browser authority.
- Midscene remains bounded visible-UX review only.
- J05 remains `RED / stopped_at_unclear_choice`.
- J06 remains `GREEN / completed_goal`.
- Playground and Puppeteer remain fail-closed stubs.
- Bugsink remains isolated and mandatory.
- Exact `{}` audit semantics remain mandatory but insufficient on their own.
- No model may overrule deterministic failure.

## Rejected for this lab

### Playwright planner/generator/healer as acceptance authority

Playwright's official agent workflow separates planning, test generation and healing, and its planner can explore an application to produce Markdown plans. [6] That is useful upstream assistance, but it would duplicate the lab's accepted catalogue and weaken the one-writer authority model. It was not added.

### Midscene Gherkin as a second execution DSL

Midscene supports Gherkin scenarios and runtime data structures. [7] Adding it here would create a second journey representation without removing the existing Playwright authority. The lab keeps Markdown intent plus executable Playwright tests and bounded Midscene judgement.

### OpenAI Symphony

Symphony turns project work into isolated, autonomous coding runs and explicitly presents its current implementation as a reference with known gaps. [8] That is an orchestration system, not a missing test primitive. It would add more lifecycle and state machinery than it removes.

### Quint model-based testing

Quint can generate traces and use them as test scenarios, including through simulator and integration-test flows. [9] The current state machine is still small enough that explicit domain, persistence, API and browser checks are clearer. Quint is deferred until the state graph or concurrency model becomes too large for direct tests.

### Showboat as a dependency

Showboat produces executable evidence documents from commands and screenshots. [10] The principle is already covered by UUID-bound logs, manifests, hashes, screenshots, JSON reports and hostile review. Adding another evidence format would duplicate the chain.

### ts-rest and broader contract frameworks

ts-rest provides a TypeScript contract layer and can generate OpenAPI from that contract. [11] This lab is plain JavaScript with one small local API. Adding TypeScript and a second contract representation would increase code paths and duplicated models.

### Queue, outbox, workflow engine and distributed idempotency machinery

The demonstrated defect was a single-process stale snapshot across an `await`. Re-reading state at the mutation boundary closes that defect. A queue, transactional outbox, operation-ID store or workflow engine would be premature until the lab contains irreversible side effects, retries across process boundaries or multiple writers.

## Deferred triggers

Revisit these only when a trigger exists:

- **operation IDs / durable deduplication:** an endpoint initiates an irreversible or externally retried side effect;
- **database transaction or compare-and-set:** the lab admits multiple server processes or independent writers;
- **model-based testing:** the explicit transition graph becomes difficult to enumerate and review;
- **generated contract tooling:** client and server schemas begin to drift in practice;
- **planner/generator agents:** they demonstrably remove more catalogue maintenance than they add, while the accepted authority remains singular.

## Sources

[1] [Evaluating AGENTS.md: Are Repository-Level Context Files Helpful for Coding Agents?](https://arxiv.org/html/2602.11988v3)  
[2] [TDDev: An Agentic Framework for Test-Driven Development](https://arxiv.org/abs/2605.17242)  
[3] [TestSuiteBench](https://arxiv.org/abs/2610.13065)  
[4] [Skeleton-Guided Program Synthesis with Large Language Models](https://arxiv.org/abs/2610.38214)  
[5] [ParallACT](https://arxiv.org/abs/2611.00314)  
[6] [Playwright Test Agents](https://playwright.dev/docs/test-agents)  
[7] [Midscene Gherkin-style Scripts](https://midscenejs.com/advanced/bdd-style-scripts-with-gherkin)  
[8] [OpenAI Symphony reference implementation](https://raw.githubusercontent.com/openai/symphony/main/elixir/README.md)  
[9] [Quint model-based testing](https://quint.sh/docs/model-based-testing)  
[10] [Showboat](https://github.com/simonw/showboat)  
[11] [ts-rest](https://ts-rest.com/)  
[12] [Anthropic: Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)  
[13] [OpenAI: Harness engineering](https://openai.com/index/harness-engineering/)  
[14] [Martin Fowler: Are harnesses worth the cost?](https://martinfowler.com/articles/are-harnesses-worth-the-cost.html)  
[15] [METR: Updated early-2025 productivity experiment](https://metr.org/blog/2026-02-24-uplift-update/)
