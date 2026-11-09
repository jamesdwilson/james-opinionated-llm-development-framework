# Raw Astra-high intake analysis

This preserved report is source evidence and analysis history, not the lab's governing decision record. `RESEARCH.md` contains the reconciled accepted, rejected and deferred decisions and explicitly resolves later adversarial findings.

## Executive verdict

**Admit no new dependencies or workflow frameworks.** The smallest useful delta is to strengthen the existing acceptance machinery, reconcile contradictory documents, and investigate one specific concurrency defect with a reproducer.

The intake’s core prescription already exists here: persistent intent, bounded work, domain/API contracts, deterministic browser checks, isolated error-delivery verification, and candidate-bound evidence.

Read-only verification matched **74 local non-dependency manifest files and all 37 artifacts referenced by 16 gate6 execution records**. Their before/after manifests agree on:

`5c78116bdfa89d4eb32cdd43197a704ee1258b85c977159f2a6205a1083015a9`

This corroborates the preserved baseline; it is **not a fresh acceptance run** or a rehash of external runtimes/dependencies. No files were changed, packages installed, package scripts run, or contributor code executed.

Requested model configuration: `gpt-6-astra` / high. Effective routing is not independently exposed in this session.

## Source-check corrections

Sources were checked on **2026-11-08 CST / 2026-11-09 UTC**. Dates below are publication/revision dates where available; rolling documentation is identified separately.

| Claim | Finding and qualification |
|---|---|
| AGENTS.md increases costs by “more than 20%” | **Narrow the claim.** The September 29 v3 reports average increases of **20% and 23% for generated files** across its two benchmarks; developer-written files increased cost by at most 19%. Neither category significantly improved resolution against no context file. This does not justify removing essential local constraints. [Paper](https://arxiv.org/html/2602.11988v3) |
| TDDev improves accuracy 15.5–23.7 percentage points | **Supported.** September 16 revision; 20 applications; ASE acceptance recorded. This concerns acceptance-testing/repair configurations and tester quality, not proof that strict unit-by-unit TDD always wins. [Paper](https://arxiv.org/abs/2605.17242) |
| TestSuiteBench and Skeleton Coding | **Numbers supported, generalization limited.** October 9 TestSuiteBench reports 165 applications, mutation scores below 60%, and 88% valid tests. October 28 Skeleton Coding reports 48.4% relative error reduction for its best configurations. Neither establishes this lab needs a new framework. [TestSuiteBench](https://arxiv.org/abs/2610.13065), [Skeleton Coding](https://arxiv.org/abs/2610.38214) |
| CAID and ParallACT | **Supported, but the intake supplies only CAID’s citation.** CAID’s July 8 revision acknowledges higher cost without substantial runtime reduction. ParallACT, submitted October 30, studies independently motivated, sometimes contradictory tasks. Add its separate citation. [CAID](https://arxiv.org/html/2603.21489v2), [ParallACT](https://arxiv.org/abs/2611.00314) |
| Practitioner TDD/harness claims | Willison’s red/green advice is practitioner guidance. Böckeler’s exploratory result is accurately summarized, but the retrieved article did not expose its claimed August publication date. Jain’s **October 13** account supports the 10/10 versus 3/10 results and roughly threefold frontier-model runtime increase; disclose that he founded Specmatic. These are limited experiments, not universal productivity findings. [Willison](https://simonwillison.net/guides/agentic-engineering-patterns/red-green-tdd/), [Böckeler](https://martinfowler.com/articles/exploring-gen-ai/tdd-in-the-agent-loop.html), [Jain](https://martinfowler.com/articles/are-harnesses-worth-the-cost.html) |
| Harness engineering, evolving specs, executable review | OpenAI’s February 11 account, Anthropic’s engineering account, Breunig’s March 4 experiment, and Meta’s October 29 deployment report support useful practices. They remain **practitioner/company accounts**; Meta’s internal system is not established as an adoptable FOSS dependency. [OpenAI](https://openai.com/index/harness-engineering/), [Anthropic](https://www.anthropic.com/research/effective-harnesses-for-long-running-agents), [Breunig](https://www.dbreunig.com/2026/03/04/the-spec-driven-development-triangle.html), [Meta](https://engineering.fb.com/2026/10/29/security/catching-bugs-before-they-land-jittestings-human-on-the-loop-approach-at-full-scale/) |
| METR caution | **Supported.** February 24 update explicitly describes selection and measurement problems. Neither its earlier slowdown nor newer estimates establish a timeless productivity effect. [METR](https://metr.org/blog/2026-02-24-uplift-update/) |
| OpenSpec/Spec Kit as preferred starting points | Their organizational capabilities are real. “Best default” and the proposed adoption order are **the intake author’s judgments**. OpenSpec validation checks specification artifacts; Spec Kit convergence remains an agent workflow, not independent execution evidence. [OpenSpec CLI](https://raw.githubusercontent.com/Fission-AI/OpenSpec/main/docs/cli.md), [Spec Kit](https://raw.githubusercontent.com/github/spec-kit/main/README.md) |
| Playwright healer can skip broken functionality | **Confirmed in current official documentation.** The lab already rejects skipped browser results and validates exact browser test identities. Extend protection to Bun tests and changed assertions rather than adding a healer. [Playwright agents](https://playwright.dev/docs/test-agents) |
| Symphony supports five trackers | **Confirmed in the current Elixir README**, which is the better citation than the intake’s SPEC link. It also explicitly calls the implementation evaluation-only prototype software. [Reference implementation](https://raw.githubusercontent.com/openai/symphony/main/elixir/README.md) |
| Quint and Showboat | Quint explicitly separates model correctness from implementation correspondence; parts of its MBT tutorial are deprecated. Its LLM kit remains experimental. Showboat verification compares rerun outputs and **skips image blocks**; it does not independently establish screenshot correctness or preserve every failed attempt. [Quint MBT](https://quint.sh/docs/model-based-testing), [LLM kit](https://github.com/quint-co/quint-llm-kit), [Showboat](https://github.com/simonw/showboat) |
| BDD proposal’s Midscene documentation criticism | **Stale.** Current guide, marked updated October 27, explicitly documents separate `aiAct`/`aiAssert` calls and Beta status. Installed 1.17.4 code independently confirms stepwise execution. The tagged raw-source URL was inaccessible in this session; no remote code was executed. [Current guide](https://midscenejs.com/advanced/bdd-style-scripts-with-gherkin) |
| Architecture checks enforce authorization | **Overstated if interpreted behaviorally.** dependency-cruiser checks dependency relationships; importing an authorization module does not prove authorization executes correctly. Retain denial tests. [Official repository](https://raw.githubusercontent.com/sverweij/dependency-cruiser/main/README.md) |
| Licensing/maintenance qualifications | Confirmed: Serena application GPL-3.0-or-later, SolidLSP MIT; GitNexus noncommercial restrictions; Task Master MIT plus Commons Clause; Context7’s supporting backend is private; Specmatic has edition boundaries; ts-rest explicitly discontinued maintenance. GPL itself is not a reason to call Serena non-FOSS. [Serena](https://raw.githubusercontent.com/oraios/serena/main/LICENSE), [GitNexus](https://raw.githubusercontent.com/abhigyanpatwari/GitNexus/main/LICENSE), [Task Master](https://raw.githubusercontent.com/eyaltoledano/claude-task-master/main/LICENSE), [Context7](https://raw.githubusercontent.com/upstash/context7/master/README.md), [Specmatic](https://docs.specmatic.io/references/open-source-vs-enterprise), [ts-rest](https://ts-rest.com/) |

Rolling documentation establishes capabilities, **not exact-version Bun compatibility, quarantine eligibility, or local acceptance**. No newly proposed dependency cleared those gates in this research.

## Existing-lab coverage map

| Need/method | Existing owner | Assessment |
|---|---|---|
| Persistent specification / SDD | `NORTH_STAR.md`, `JOURNEY_CATALOG.md`, `ACCEPTANCE_MATRIX.md` | **Already covered.** Governing journey catalog is missing from candidate hashing. |
| Bounded ticket and continuity | `project-record.json` | **Already covered.** Keep one execution-state authority; link accepted scope rather than create another task database. |
| Contracts | `src/domain.mjs`, `src/server.mjs`, domain/API/persistence tests | **Already covered for this bounded application.** HTTP examples are not an exhaustive response schema or portable OpenAPI contract. |
| BDD / specification by example / ATDD | J01–J06 and deterministic Playwright tests | **Already covered as practices.** Gherkin execution remains proposed. |
| TDD and test effectiveness | Preserved RED/GREEN evidence, targeted mutations, hostile closure review | **Already covered in part.** Test count alone proves neither coverage nor regression sensitivity. |
| Browser and visible UX | Playwright 1.63.0; bounded Midscene 1.17.4 observer | **Already covered.** Keep deterministic authority and optional UX judgment distinct. |
| Error delivery and cleanup | Isolated Bugsink 2.6.3, exact readback, five failure injections | **Already covered.** Protected 2.1.2/8100 is outside modification scope. |
| Reproducible completion | `candidate.mjs`, `record-run.mjs`, `closure-gate.mjs`, hashed artifacts | **Already covered, with narrow gaps below.** No report framework needed. |
| Architecture | Pure domain; SQLite repository; HTTP composition; browser code | **Useful document-only clarification.** No demonstrated need for a graph tool. Server reuse of browser-safe `parseDsn` is intentional, not automatically a forbidden edge. |
| Properties/concurrency | Sequential approval idempotency and provenance examples | **Partial.** No generated property suite or controlled overlapping-request test was found. |
| Dependency governance | Bun pin, `bun.lock`, overrides/stubs, audit, research manifests | **Already covered.** Historical npm lock is not the current installation authority. |

The application is currently small JavaScript modules with TypeScript browser tests. **Elysia/Eden, Hono RPC, oRPC and application Zod contracts are not installed architecture choices.** The Zod override belongs to Midscene’s dependency graph.

## Admit now

“Admit” here means recommend for the next authorized implementation batch.

1. **Bind accepted intent to candidate identity.**  
   [`scripts/candidate.mjs:6`](/Users/james/.hermes-next-v0.22.4/cache/scratch/full-stack-methodology-lab/scripts/candidate.mjs:6) includes North Star and acceptance matrix but omits `JOURNEY_CATALOG.md`. Add that existing authority rather than installing OpenSpec.

2. **Protect accepted checks and complete the existing recorder.**  
   [`closure-gate.mjs:171`](/Users/james/.hermes-next-v0.22.4/cache/scratch/full-stack-methodology-lab/scripts/closure-gate.mjs:171) accepts a consistent positive Bun summary without requiring the accepted test identities. A reduced suite could therefore qualify on a newly sealed candidate. Also, `record-run.mjs` lacks the audit-specific artifact/verification branch required by closure. Fix these existing components; do not add Showboat.

3. **Admit a focused concurrency reproducer, with repair conditional on meaningful RED.**  
   [`server.mjs:118`](/Users/james/.hermes-next-v0.22.4/cache/scratch/full-stack-methodology-lab/src/server.mjs:118) reads task state **before** awaiting the request body. Two overlapping requests can consequently compute transitions from stale state. Predicted consequences include duplicate approval events or a delayed completion request overwriting later progress. **This is source-based inference, not an executed finding.**

No newly removed or weakened local test bytes were found relative to the accepted manifest. The check-preservation recommendation addresses a future acceptance gap, not evidence that gate6’s 43 passing tests were fabricated.

## Document-only updates

| Files | Smallest correction |
|---|---|
| `ACCEPTANCE_REPORT.md`, `STACK_VERSION_MATRIX.md`, `codex-result.txt` | Clearly label superseded status and point to `LAB_CLOSURE_VERDICT.md`. Preserve historical failed evidence; do not rewrite it as success. |
| `LLM_POLICY.md`, `scripts/bugsink/README.md`, `CODEX_BRIEF.md` | Distinguish historical instructions from current Bun/2.6.3 operation. The Bugsink README still describes 2.1.2 and removed middleware. Mark the Node-based, source-mutating `scripts/repair-mutations.py` obsolete; do not invoke it as a current gate. |
| `STACK_ECOSYSTEM_RESEARCH.md` | Make its framework preferences conditional and subordinate to the later locked “less” decisions. Replace speculative ts-rest inactivity wording with its explicit maintenance notice. |
| `ACCEPTANCE_MATRIX.md`, `project-record.json` | Put the accepted change contract in the existing matrix: scope, requirement links, non-goals, affected boundaries, evidence and stop conditions. Let the project record reference it and retain execution state. |
| `NORTH_STAR.md`, journey/BDD documents | Record an unresolved distinction: North Star forbids **creator** self-approval; implementation forbids the **completer** from approving. Existing examples generally make these the same person. Do not silently resolve the creator≠completer case by rewriting expectations to match code. |
| `BDD_REASONING_SUITE_PROPOSAL.md`, `bdd/JOURNEY_CATALOG.proposed.json` | Preserve `proposed_for_review`. Correct R01: creation produces `open`; waiting requires a completion request. Make R03/R04 fixtures name both creator and completer. Remove stale documentation/model-recommendation claims. R06’s pre-commit retry does not establish retry safety after an uncertain successful commit. |
| New intake addendum under `research/` | Preserve this source/disposition analysis separately from the already hashed community research. Avoid changing historical ledgers merely to make them agree with later findings. |

A document-only change can still change the exact candidate; see below.

## Defer/reject table

| Tool | Classification | Lab-specific reason / reconsideration trigger |
|---|---|---|
| OpenSpec; Spec Kit | **Reject as overlap/overkill** | Existing specification and acceptance artifacts already own intent. Reconsider only if a bounded replacement removes more machinery than it introduces. |
| Superpowers | **Reject as overlap/overkill** | Planning, TDD, review and verification already exist; importing another mandatory workflow adds competing instructions. |
| Backlog.md; Beads | **Reject as overlap/overkill** | A second task authority is unnecessary. Current Beads also introduces Dolt operations. |
| Serena | **Defer until a demonstrated gap** | Four server modules do not establish a symbol-navigation problem. Revisit measured repeated exploration or missed references. |
| Zod + oRPC | **Defer until a demonstrated gap** | No separately maintained typed client or duplicated schema corpus presently warrants migration. Choose one contract owner if that changes. |
| Schemathesis; oasdiff | **Defer until a demonstrated gap** | No accepted OpenAPI artifact exists. Do not introduce one solely to feed these tools. Revisit external consumers or demonstrated schema/compatibility defects. |
| Specmatic; Pact | **Defer until a demonstrated gap** | No independently released consumer/provider boundary. Pact does not inherently require a broker; its value still needs an actual compatibility problem. |
| Playwright-BDD / Cucumber | **Reject as overlap/overkill** | J01–J06 already express examples and executable acceptance. No demonstrated stakeholder need for another maintained representation. |
| Midscene Gherkin / separate Midscene runner | **Experimental spike only** | Expands beyond the accepted observer route into AI actions. Proposal defects and calibration requirements must be resolved first. |
| fast-check | **Defer until a demonstrated gap** | Start with fixed actor/state tables and controlled request interleavings. Admit generation/shrinking when those become insufficient. |
| StrykerJS | **Experimental spike only** | Targeted mutation is useful; a broad engine is not yet justified. Official command-runner support does not prove the complete engine runs correctly under Bun 1.4.4. |
| dependency-cruiser | **Defer until a demonstrated gap** | Document the tiny import boundary first. Reconsider actual drift or graph complexity; avoid building a homegrown parser meanwhile. |
| Quint / Quint LLM Kit | **Experimental spike only** | Consider a genuinely difficult stateful protocol with implementation-trace correspondence. This application’s small state machine does not yet justify another specification language. |
| Showboat | **Reject as overlap/overkill** | Existing runner records and closure provide stronger candidate-specific evidence. Improve their replay instructions and audit recording. |
| Harbor | **Experimental spike only** | Useful for repeated comparative workflow evaluation, not routine application acceptance. First define representative tasks, independent graders and cost accounting. |
| Symphony | **Reject as overlap/overkill** | Adds another queue executor/control plane, plus prototype operational scope. It must not compete with the existing execution owner. |
| Stagehand | **Reject as overlap/overkill** | No changing external website to automate. Browserbase itself recommends Playwright for an owned stable application in CI. |
| Plumb | **Experimental spike only** | Consequential decision review is useful; automated spec rewriting must not become acceptance authority. |
| ts-rest | **Reject for maintenance reasons** | Upstream explicitly disclaims future fixes/security support. |
| GitNexus; Task Master | **Reject for license reasons** | Do not fit an unrestricted FOSS shortlist. |
| Context7 | **Defer until a demonstrated gap** | Direct primary-source retrieval suffices; it is not a fully self-hostable FOSS documentation stack. |
| Open/unmerged remediation, including Midscene #3358 | **Reject for source reasons** | Metadata/diff evidence only. It remained open when checked; no execution, copying or porting. |

## Exact TDD implementation plan

These are proposed future steps. **No RED/GREEN run occurred during this analysis.**

| Change | Observable contract and truthful baseline | Smallest implementation | Focused tests and exact stop |
|---|---|---|---|
| **D0 — reconcile authority/status** | Baseline is documentary contradiction, not failing application behavior. | Update the documents above; preserve historical evidence and locked research. No new tracker. | Cross-check commands, pins, statuses and links against actual package/scripts and gate6 records. Stop when current instructions have one unambiguous authority and unresolved product decisions are explicitly marked. |
| **D1 — bind journey specification** | Any accepted journey change changes candidate identity; missing governing input fails closed. Current path list omits the catalog. | Add `JOURNEY_CATALOG.md` to `candidatePaths`; add focused coverage in `test/closure.test.mjs` or a small candidate test. Keep volatile queue/status fields outside the content fingerprint. | In disposable fixtures, demonstrate catalog edits change identity and stale records fail. First observe failure on the old implementation. Stop when those cases pass and unchanged fixtures retain stable identity. |
| **D2 — prevent check erosion and record audits** | A passing summary cannot substitute for the accepted executed checks. A recorder-produced audit record must satisfy closure’s existing command/artifact contract. Current Bun verifier lacks identity inventory; recorder lacks audit support. | Extract only necessary pure verification functions from `closure-gate.mjs`; maintain one reviewed check inventory, replacing existing browser-title duplication. Extend `record-run.mjs` to bind audit output and verification status. Surface changed acceptance-test/config files against the previous manifest for independent review. | RED fixtures: removed test with coherent lower totals; skipped/todo/only-reduced run; duplicated/substituted identities; missing audit JSON; nonempty or malformed audit. Characterize genuine gate6 logs as valid. Stop when all negative fixtures fail closed, genuine records pass, and changed assertions receive independent disposition. Do not claim identity checks detect weakened assertions automatically. |
| **D3 — characterize overlapping transitions** | Repeated approval must not add events; delayed requests must not overwrite later completed state. Existing sequential examples are green; concurrent behavior is unexecuted. | Add two controlled HTTP interleavings to `test/api.test.mjs`: overlapping approvals, and a delayed completion overtaken by completion/approval. If RED confirms the hypothesis, reread authoritative state after body consumption and keep transition/save synchronous in this single-process architecture. Preserve existing error precedence. | Use request/body barriers, not timing sleeps. Assert exact statuses, idempotency, timestamps and event lineage. Run `bun test test/api.test.mjs test/domain.test.mjs test/persistence.test.mjs`. Stop without production edits if the hypothesis is disproved; otherwise stop after both regressions and existing contracts pass. No distributed-locking framework. |

For D2, the accepted inventory must **not be regenerated automatically from the changed suite**. Additions/removals require an explicit acceptance-contract decision. Source hashes and independent review expose same-named tests whose assertions were weakened.

Broad gates for every executable delta are the fresh sequence below. Also run the existing scanner regression suite separately; it is not included in the “43 Bun tests” count.

## Candidate invalidation and acceptance plan

The current candidate includes `src/`, `public/`, `scripts/`, `test/`, `e2e/`, `research/`, `stubs/`, dependencies, both locks, selected policies/configuration, Bun, the isolated Python environment and Chromium.

Therefore **all D1–D3 changes invalidate it**, as do:

- edits to `NORTH_STAR.md`, `ACCEPTANCE_MATRIX.md`, `LLM_POLICY.md`;
- any new research files under `research/`;
- dependency, override, stub, runtime or browser changes;
- review-prompt or model-policy changes.

Currently excluded root reports, `project-record.json`, the journey catalog and proposed BDD files do not mechanically alter the fingerprint. That exclusion is **not permission to change accepted behavior without reevaluation**. D1 closes the journey-catalog omission. Output/status records should remain outside the fingerprint to avoid self-invalidation.

After all admitted bytes and expectations are finalized:

1. Preserve focused RED or explicitly labeled characterization evidence. Freeze a new candidate.
2. Record **two independent complete Bun runs** and **two Chromium runs** through the existing recorder. Require the reviewed test inventory, zero failures/skips/todos, and zero browser flakiness. The new Bun count may exceed 43.
3. Record **two isolated Bugsink 2.6.3 successes**, fresh state and exact readback/recovery/cleanup.
4. Record all five injected modes: `bootstrap`, `callback`, `already-exited`, `output`, `response`. Require expected exit 1 **and** matching `failureMode`, `failureReached`, cleanup and clean bounded scan.
5. For this lab’s full closure, record **two J05/J06 pairs** on that exact candidate. J05 must reject the ambiguous control; J06 must complete with no visible contradictions; `UNCLEAR` cannot pass. This does not make Midscene a universal product gate.
6. Record fresh `bun audit --json`, exact plain `{}`, successful exit, and bound artifacts. Retain exact pins and seven-day quarantine. No graph change is recommended.
7. Run the existing Python scanner regressions and retain their separate execution evidence.
8. Require unchanged before/after manifests, closure with no blocks, and independent hostile review covering check removals/weakening, evidence semantics and the concurrency repair.

**Stop on any unexplained failure, missing evidence, unauthorized expectation change, or candidate drift.** Repair first, then restart the complete sequence after final bytes are stable. Never reuse old-candidate passes or treat an infrastructure exit 1 as proof that an injection was reached.

Port 8100 remains observational only; no connection, signal, migration or configuration change targets its Bugsink 2.1.2 instance.

## Sources (direct URLs)

Publication dates and corrections appear above. The following additional official capability sources were opened during this review; these are rolling sources accessed November 9 UTC, not validated installation pins.

| Area | Direct sources |
|---|---|
| Specifications and work state | [OpenSpec](https://raw.githubusercontent.com/Fission-AI/OpenSpec/main/README.md), [Spec Kit](https://raw.githubusercontent.com/github/spec-kit/main/README.md), [Superpowers](https://raw.githubusercontent.com/obra/superpowers/main/README.md), [Backlog.md](https://raw.githubusercontent.com/MrLesk/Backlog.md/main/README.md), [Beads/Dolt](https://raw.githubusercontent.com/gastownhall/beads/main/README.md) |
| API contracts | [oRPC explicit contracts](https://orpc.dev/docs/contract/procedure), [Schemathesis](https://raw.githubusercontent.com/schemathesis/schemathesis/master/README.md), [oasdiff](https://github.com/oasdiff/oasdiff), [Pact](https://docs.pact.io/), [Specmatic editions](https://docs.specmatic.io/references/open-source-vs-enterprise) |
| Test effectiveness and boundaries | [fast-check properties](https://fast-check.dev/docs/introduction/why-property-based/), [model-based testing](https://fast-check.dev/docs/advanced/model-based-testing/), [StrykerJS runners](https://stryker-mutator.io/docs/stryker-js/guides/nodejs/), [dependency-cruiser](https://raw.githubusercontent.com/sverweij/dependency-cruiser/main/README.md), [Playwright-BDD](https://raw.githubusercontent.com/vitalets/playwright-bdd/main/README.md) |
| Frontier tools | [Quint correspondence limits](https://quint.sh/docs/model-based-testing), [Quint LLM Kit](https://github.com/quint-co/quint-llm-kit), [Showboat verification](https://github.com/simonw/showboat), [Harbor/Docker](https://raw.githubusercontent.com/harbor-framework/harbor/main/README.md), [Symphony reference implementation](https://raw.githubusercontent.com/openai/symphony/main/elixir/README.md) |
| Browser scope and upstream status | [Midscene Gherkin](https://midscenejs.com/advanced/bdd-style-scripts-with-gherkin), [Stagehand’s CI qualification](https://www.browserbase.com/stagehand), [Midscene PR #3358—open metadata only](https://github.com/web-infra-dev/midscene/pull/3358) |