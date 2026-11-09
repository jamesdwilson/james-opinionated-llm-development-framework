The strongest approach for this goal is **a persistent specification, a tightly scoped ticket, executable contracts, and independent verification around the coding agent**. That combination addresses different kinds of drift: building the wrong feature, changing an interface accidentally, violating business rules, and declaring completion without sufficient evidence.

The useful umbrella term is **harness engineering**: designing the context, tools, execution rules, and feedback that surround the model. Both OpenAI's and Anthropic's engineering accounts emphasize this surrounding infrastructure when describing reliable, extended agent work. Those are practitioner accounts, however, rather than controlled proof of universal productivity gains. [OpenAI](https://openai.com/index/harness-engineering/?trk=article-ssr-frontend-pulse_x-social-details_comments-action_comment-text\&utm_source=chatgpt.com)

**The most interesting frontier additions are Quint, Showboat, Harbor, and Symphony.** For immediate use in a TypeScript web stack, the stronger starting point is OpenSpec or Spec Kit, explicit Zod/oRPC contracts, Playwright, and selected contract, property, and mutation tests.

Research current through **November 8, 2026**. The recommendations below distinguish published findings, practitioner opinions, and judgments based on tool capabilities. No convincing head-to-head research surfaced establishing one universal winner among OpenSpec, Spec Kit, Superpowers, or the various agent workflow frameworks.

## 1. What the research actually supports

Several recent findings materially change what deserves a place in the stack.

| Research | Finding | Practical implication |
|---|---|---|
| **Evaluating AGENTS.md**, September 2026 revision | Repository context files did not significantly improve task resolution overall, while increasing inference costs by more than 20% on average. Developer-written files performed better than generated ones, but their advantage over having no file was not statistically significant. The evaluation concerns issue resolution, principally in Python repositories. | Keep instructions specific to information the agent cannot easily discover. Automatically generating a long repository encyclopedia is not an evidence-backed default. This study does **not** establish that every instruction file is harmful. [arxiv.org](https://arxiv.org/html/2602.11988v3?utm_source=chatgpt.com) |
| **TDDev**, accepted at ASE 2026 | Across 20 full-stack applications, sufficiently capable models improved acceptance-test accuracy by **15.5 to 23.7 percentage points** with automated testing and repair. Tester reliability strongly affected results. | Executing user workflows and feeding useful failures back to the developer agent can improve requirement fulfillment. The finding supports a feedback loop; it does not prove that strict, one-unit-test-at-a-time TDD is always optimal. [arxiv.org](https://arxiv.org/abs/2605.17242?utm_source=chatgpt.com) |
| **TestSuiteBench**, October 2026 preprint | Across 165 applications, generated suites achieved mutation scores below 60%, despite 88% of generated tests passing against reference implementations. | An agent can produce working-looking software and weak tests for it. Evaluate whether tests detect incorrect behavior, rather than counting tests or accepting a green run at face value. [arxiv.org](https://arxiv.org/abs/2610.13065?utm_source=chatgpt.com) |
| **Skeleton Coding**, October 28 preprint | Supplying program structure alongside behavioral specifications reduced mean test error by **48.4% relative** in the best-performing configurations across four models and three benchmarks. | Establish important types, module boundaries, interfaces, and invariants before delegating implementation. This is promising benchmark evidence, with selected configurations, rather than a measured productivity gain for real teams. [arxiv.org](https://arxiv.org/abs/2610.38214?utm_source=chatgpt.com) |
| **CAID and ParallACT**, 2026 multiagent studies | CAID improved results using dependency-aware delegation, isolated worktrees, and controlled integration, but increased cost without substantially reducing runtime. ParallACT found severe failures when independently tasked agents combined incompatible work. | Parallelism needs interface agreements and an integration owner. Adding agents or a communication channel does not automatically resolve conflicting requirements. The studies examine different coordination setups, so their results should not be treated as contradictory. [arxiv.org](https://arxiv.org/html/2603.21489v2?utm_source=chatgpt.com) |

**The resulting design principle:** give the agent a clear target, constrain consequential interfaces, and provide feedback capable of falsifying its solution. Adding more planning stages deserves an actual evaluation.

## 2. The FOSS stack worth considering

### A. Preserve intent with one specification system

These tools help turn a conversation into persistent development inputs. Their value is organizational and procedural; their checks have different levels of authority.

| Tool | What it contributes | Recommended use |
|---|---|---|
| **[OpenSpec](https://github.com/Fission-AI/OpenSpec)**, MIT | Change-specific proposals, requirements, scenarios, design notes, and tasks, with changes incorporated into the maintained specification. | **Best default for incremental work in an existing product.** Its relatively flexible workflow suits ongoing feature development. Its `validate` command checks structural issues in specs, not whether the application actually behaves correctly. [GitHub](https://github.com/Fission-AI/OpenSpec?utm_source=chatgpt.com) |
| **[GitHub Spec Kit](https://github.com/github/spec-kit)**, MIT | Project principles, specification, clarification, implementation planning, tasks, consistency analysis, and a convergence assessment. | **Best when the team wants an explicit shared process.** The current convergence step compares implementation against the artifacts and appends missed work. That is an agent assessment, so passing executable checks still matters. [GitHub](https://github.com/github/spec-kit?utm_source=chatgpt.com) |
| **[Superpowers](https://github.com/obra/superpowers)**, MIT | Reusable execution skills for planning, TDD, debugging, worktrees, review, and completion verification. | **Useful for improving how an existing agent works.** Select the practices that solve observed failures. Its standard workflow can introduce considerable small-task and review overhead; instructions described as mandatory still depend on the agent following them. [GitHub](https://github.com/obra/superpowers?utm_source=chatgpt.com) |

For the stated goal, **OpenSpec is the first specification tool to trial**. Spec Kit is a strong alternative when project-wide principles and a more explicit progression are valuable.

Choose one authority for feature requirements. If Superpowers supplies execution skills, those skills should consume the accepted specification rather than create another competing definition of the feature.

A useful test for any specification framework is:

> Does this artifact resolve ambiguity, drive a check, or preserve a decision needed later?

If none applies, maintaining it may add work without improving delivery.

### B. Keep tickets and dependencies outside the conversation

| Tool | Contribution | When it earns its place |
|---|---|---|
| **[Backlog.md](https://github.com/MrLesk/Backlog.md)**, MIT | Markdown tickets in Git, acceptance criteria, plans, milestones, and a local task-board workflow. | **Good lightweight default** when there is no satisfactory existing tracker. Tasks remain inspectable alongside the code. Its completion fields still need verification outside the agent's own status updates. [GitHub](https://github.com/MrLesk/Backlog.md?utm_source=chatgpt.com) |
| **[Beads](https://github.com/gastownhall/beads)**, MIT | Persistent dependency graph, ready/blocked work, task claiming, structured output, and coordination across sessions. | **Better for dependency-heavy, extended agent work.** Current Beads uses Dolt as its authoritative database. Older descriptions presenting it as merely Git-tracked JSONL are outdated; database synchronization and migration add operational complexity. [GitHub](https://github.com/gastownhall/beads?utm_source=chatgpt.com) |

An existing issue tracker may already be sufficient. Adding Backlog.md, Beads, and a separate framework's task database simultaneously creates synchronization work.

The useful division is:

- **Specification:** what behavior is intended.
- **Ticket:** which bounded change is authorized now.
- **Execution record:** what happened during the attempt.
- **Verification result:** what independently passed against the resulting revision.

### C. Retrieve the relevant code precisely

**[Serena](https://github.com/oraios/serena)** is worth evaluating when agents repeatedly reread large files, miss callers, or make fragile cross-file edits.

Its open language-server integration provides symbol lookup, reference lookup, diagnostics, and symbolic editing. These capabilities can help an agent inspect the actual dependency surface of a ticket. Several richer refactorings and interactive debugging features belong to its separate paid JetBrains backend. [GitHub](https://github.com/oraios/serena?utm_source=chatgpt.com)

The current license is **GPL-3.0-or-later for the Serena application**, with **MIT for SolidLSP**. Older recommendations calling the entire current project MIT are stale. [GitHub](https://github.com/oraios/serena/blob/main/LICENSE?utm_source=chatgpt.com)

The recommendation here is selective context retrieval. A task should start with its relevant requirements, interfaces, decisions, and code references. More retrieved material should have a concrete purpose.

### D. Make interface misalignment mechanically detectable

#### Zod + oRPC: the TypeScript starting point

**[Zod](https://github.com/colinhacks/zod)** and **[oRPC](https://github.com/middleapi/orpc)** are both MIT. Zod supplies runtime schemas and inferred types. oRPC supports shared contracts, typed clients, and OpenAPI integration. [GitHub](https://github.com/colinhacks/zod?utm_source=chatgpt.com)

For agent-driven implementation, prefer **explicit contract-first inputs, outputs, and errors**. oRPC supports this approach directly. Relying entirely on types inferred from the implementation leaves more room for the implementation to define an unintended interface. [Typesafe APIs Made Simple 🪄](https://orpc.dev/?utm_source=chatgpt.com)

The important decisions extend beyond field names:

- Whether money is represented in minor units.
- Whether timestamps include a timezone.
- Whether missing and `null` mean different things.
- Which failures are retryable.
- Whether repeating a request can repeat its side effects.
- Which authorization context must accompany an operation.

A schema can enforce the rules encoded in it. Two components sharing the same incorrect schema can still agree perfectly.

**Current maintenance correction:** ts-rest's official site now says it is no longer maintained, with no planned releases, bug fixes, security updates, or support. For a new stack, oRPC deserves evaluation ahead of casually adopting ts-rest from an older recommendation. [ts-rest.com](https://ts-rest.com/?utm_source=chatgpt.com)

#### Schemathesis + oasdiff: two distinct checks

| Tool | Check it provides | Why it matters for coding agents |
|---|---|---|
| **[Schemathesis](https://github.com/schemathesis/schemathesis)**, MIT | Generates API tests from schemas, including edge cases, stateful sequences, and custom checks. | Finds cases where a running API violates its declared interface or fails under combinations the agent did not consider. Add business assertions for behavior that a schema alone cannot express. [GitHub](https://github.com/schemathesis/schemathesis?utm_source=chatgpt.com) |
| **[oasdiff](https://github.com/oasdiff/oasdiff)**, Apache-2.0 | Compares OpenAPI versions and detects breaking changes. | Catches an agent changing the contract itself to accommodate its implementation, potentially breaking existing clients. [GitHub](https://github.com/oasdiff/oasdiff?utm_source=chatgpt.com) |

Together, these ask: **Does the implementation satisfy the contract, and is changing the contract compatible with its consumers?**

For larger service boundaries, two additional options are useful:

- **[Specmatic](https://github.com/specmatic/specmatic):** its MIT core provides contract testing and mocks from API specifications. This is valuable when frontend and backend agents need to work against the same defined API. Advanced protocols and several richer testing/mocking features are enterprise products. [GitHub](https://github.com/specmatic/specmatic?utm_source=chatgpt.com)
- **[Pact](https://docs.pact.io/):** consumer-driven HTTP and message contracts, with an MIT JavaScript implementation. It becomes more valuable when services and consumers deploy independently. A small application deployed as one unit may not justify its extra coordination. [Pact Docs](https://docs.pact.io/?utm_source=chatgpt.com)

### E. Verify behavior, including the tests themselves

#### Playwright + selective Midscene

**Playwright should handle the important repeatable browser checks.** Its current agent tooling includes a planner, test generator, and healer, so agents can help author and maintain conventional browser tests. [Playwright](https://playwright.dev/docs/test-agents?utm_source=chatgpt.com)

**[Midscene.js](https://github.com/web-infra-dev/midscene)**, MIT, adds screenshot-based interaction and natural-language assertions. It integrates with Playwright and supports other platforms. It is particularly interesting for canvas interfaces, custom controls, native applications, and checking visible states that are awkward to address through ordinary selectors. [GitHub](https://github.com/web-infra-dev/midscene?utm_source=chatgpt.com)

A practical division:

| Verification need | Preferred approach |
|---|---|
| Exact amount, permission, persisted state, API response | Explicit code assertions |
| Stable critical user journey | Playwright regression test |
| Exploratory navigation and unusual visual controls | Midscene |
| Visual assessment requiring interpretation | Midscene, with captured evidence and calibrated expectations |

For important numeric or authorization results, a visual model's judgment should not be the only acceptance signal.

**A concrete self-healing trap:** Playwright's healer documentation permits a skipped test when the healer believes functionality is broken. Configure CI to flag newly skipped tests, and treat changes to expected outcomes or removed assertions as consequential changes. Otherwise, automated repair can conceal a product regression. [Playwright](https://playwright.dev/docs/test-agents?utm_source=chatgpt.com)

**[Stagehand](https://www.browserbase.com/stagehand)** is a useful MIT alternative for agents operating changing external websites. Browserbase's own documentation says Playwright remains the better fit for testing an application's own stable UI in CI. Its hosted infrastructure is a separate product. [Browserbase](https://www.browserbase.com/stagehand?utm_source=chatgpt.com)

#### fast-check + StrykerJS: particularly valuable with generated code

**[fast-check](https://github.com/dubzzz/fast-check)**, MIT, generates inputs and action sequences to test properties, then reduces failures to smaller examples. It supports model-based testing of stateful behavior. [GitHub](https://github.com/dubzzz/fast-check?utm_source=chatgpt.com)

Useful properties might include:

- Retrying an operation does not create another order.
- Serialization and parsing preserve the relevant information.
- A user cannot access another tenant's resources.
- Canceling a reservation releases capacity exactly once.
- Sorting changes order without losing or duplicating elements.

The property must come from the requirement. Reimplementing the same algorithm inside the test can reproduce the same mistake.

**[StrykerJS](https://github.com/stryker-mutator/stryker-js)**, Apache-2.0, deliberately changes implementation logic and checks whether tests detect those changes. It is a strong addition when an agent generates a large test suite whose assertions may be weak. [GitHub](https://github.com/stryker-mutator/stryker-js?utm_source=chatgpt.com)

Apply mutation testing to important changed logic. Requiring a universal 100% score can create substantial runtime and maintenance overhead, including work on mutations that do not meaningfully change behavior.

#### Architecture checks

**[dependency-cruiser](https://github.com/sverweij/dependency-cruiser)**, MIT, turns dependency rules into executable checks. It can detect prohibited imports, dependency cycles, and violations of declared module boundaries. [GitHub](https://github.com/sverweij/dependency-cruiser?utm_source=chatgpt.com)

This is an effective way to enforce rules such as:

- UI components must not access the database directly.
- Domain logic must not depend on framework-specific adapters.
- A feature must use the shared authorization component.
- A module's internal implementation must not become a public dependency.

These checks make architectural drift visible without asking another model to interpret the same architecture document on every change.

## 3. Four frontier tools especially worth investigating

### 1. Quint: executable models for difficult business behavior

**[Quint](https://github.com/quint-co/quint)** and **[Quint LLM Kit](https://github.com/quint-co/quint-llm-kit)** are Apache-2.0 projects. Quint describes state, transitions, and invariants in an executable specification language. The LLM kit provides tools and agent workflows for creating and checking those specifications. [github.com](https://github.com/quint-co/quint?utm_source=chatgpt.com)

This is the most interesting advanced addition when correctness depends on sequences and concurrency:

- Retrying payments or jobs.
- Reserving limited inventory.
- Approval and cancellation workflows.
- Distributed ownership or locking.
- Recovery after partial failure.

A model can express rules such as “a completed order cannot return to pending” or “two successful reservations cannot consume the same final unit.” The checker can search for sequences that violate the rule.

**The crucial limitation is correspondence with real code.** Verifying the model does not establish that the implementation follows it. Quint's documentation explicitly recommends model-based testing and trace validation to improve confidence in that correspondence, while acknowledging that those do not prove production-code correctness. [Quint Docs](https://quint.sh/docs/model-based-testing?utm_source=chatgpt.com)

The LLM kit is experimental and explicitly says it has not been thoroughly evaluated for general public use. Trial it on one difficult workflow before making it a project-wide dependency. [github.com](https://github.com/quint-co/quint-llm-kit?utm_source=chatgpt.com)

### 2. Showboat: make completion inspectable and reproducible

**[Showboat](https://github.com/simonw/showboat)**, Apache-2.0, creates executable Markdown demonstrations containing commands, captured output, commentary, and images. Its verifier can rerun the code blocks and compare results. [GitHub](https://github.com/simonw/showboat?utm_source=chatgpt.com)

This directly addresses vague completion claims.

A ticket's deliverable can include:

- A command demonstrating the original problem.
- The same operation succeeding after the change.
- Relevant API responses.
- A browser screenshot.
- An explicit demonstration of an important failure case.

This gives the next agent and the reviewer usable evidence without requiring them to reconstruct the whole session.

Its limitation is straightforward: an executable demonstration proves only what it exercises. It can still omit the difficult case. Run it in a controlled environment, and retain independent acceptance checks.

### 3. Harbor: benchmark the development workflow itself

**[Harbor](https://github.com/harbor-framework/harbor)**, Apache-2.0, evaluates agents in containerized task environments. It supports existing agents and custom benchmarks, including local Docker execution. [GitHub](https://github.com/harbor-framework/harbor?utm_source=chatgpt.com)

This is the strongest answer to claims that a plugin, context file, or workflow pack makes agents dramatically better: test that claim on representative work.

Build a small evaluation set from actual tickets:

- A bug with an existing reproducer.
- A cross-layer feature.
- An API compatibility change.
- A stateful workflow.
- A migration.
- A task with deliberately explicit non-goals.

Compare the existing workflow with one proposed addition at a time. Use the same acceptance checks and repeat enough tasks to see whether an apparent improvement persists.

Harbor provides the execution infrastructure. A representative task set and credible grading remain the team's responsibility.

### 4. Symphony: autonomous execution from the ticket queue

**[Symphony](https://github.com/openai/symphony)**, Apache-2.0, moves orchestration toward a continuously running service: read eligible issues, create per-issue workspaces, launch agents, and apply repository-owned workflow policy. The current reference implementation documents adapters for Linear, GitHub Issues, Jira Cloud, Asana, and GitLab. [GitHub](https://github.com/openai/symphony/blob/main/SPEC.md?utm_source=chatgpt.com)

This closely matches the desired operating model: maintain goals and tickets at a high level while bounded execution happens automatically.

Its value is operational:

- Work selection.
- Workspace isolation.
- Concurrency and retries.
- Workflow configuration.
- Observability and handoff.

The reference implementation is explicitly prototype software intended for evaluation. A scheduler also cannot determine whether an ambiguous ticket represents the right product decision. Introduce this layer after the task contracts and verification process work reliably. [GitHub](https://github.com/openai/symphony?utm_source=chatgpt.com)

## 4. The methodologies fit together at different levels

SDD, BDD, TDD, and contract testing are useful for different decisions. Treating them as substitutes leaves gaps.

| Method | Question it helps answer | Appropriate artifact |
|---|---|---|
| **Specification-driven development** | What should this feature accomplish, and what constraints matter? | Accepted requirements, non-goals, interface decisions |
| **BDD / specification by example** | What does correct behavior mean in concrete situations? | Domain examples, including exceptions |
| **Acceptance-test-driven development** | What observable behavior establishes that the ticket is complete? | Executable acceptance checks |
| **TDD** | Does the next implementation change satisfy the behavior currently being developed? | Focused failing test followed by implementation and refactoring |
| **Contract testing** | Do separately implemented components agree at their boundaries? | API/message schemas and consumer/provider checks |
| **Property-based and model-based testing** | Which rules must remain true across many inputs or sequences? | Invariants and a simpler behavioral model |
| **Mutation testing** | Would the tests notice plausible incorrect implementations? | Mutation results and improved assertions |
| **Architecture checks** | Does the change preserve important dependency boundaries? | Executable dependency rules |

For BDD specifically, **[Playwright-BDD](https://github.com/vitalets/playwright-bdd)**, MIT, is worth considering. It connects readable `Given / When / Then` scenarios to the Playwright runner. That creates a useful route from stakeholder-readable examples to executed browser checks. [GitHub](https://github.com/vitalets/playwright-bdd?utm_source=chatgpt.com)

Use Gherkin when people actually read and refine the scenarios. If only agents maintain both the prose and the step definitions, the extra representation needs to justify its maintenance cost.

TDD also deserves proportional use. A focused regression test is highly useful for a bug fix. Applying an elaborate test-first ritual to a wording change or straightforward layout adjustment can cost more than it contributes.

## 5. The informal hot takes worth taking seriously

### Simon Willison: give agents a red/green test loop

Willison recommends the compact instruction **“Use red/green TDD”** and emphasizes confirming failure before implementation. The useful mechanism is that the agent gets executable feedback while working. This is experienced practitioner guidance, rather than a controlled study. [Simon Willison's Weblog](https://simonwillison.net/guides/agentic-engineering-patterns/red-green-tdd/?utm_source=chatgpt.com)

### Birgitta Böckeler: strict TDD inside the agent loop may add little

Her August 2026 exploratory comparison found no clearly discernible quality advantage from prompting strict TDD inside the agent's own loop, and no meaningful mutation-score advantage. The experiment was small, used relatively contained greenfield tasks, and relied heavily on an LLM judge. It challenges automatic confidence in the ritual without establishing that TDD is ineffective. [theater or actual value?](https://martinfowler.com/articles/exploring-gen-ai/tdd-in-the-agent-loop.html?utm_source=chatgpt.com)

**Practical judgment:** insist on meaningful behavioral evidence. Evaluate how much incremental ceremony is necessary to obtain it.

### Naresh Jain: the same harness can help one model and burden another

In an October 2026 experiment on one Java service, a stronger model passed all 10 runs with and without the behavioral harness, while harnessed runs took roughly three times as long. A smaller model improved from 3 successful runs out of 10 to 10 out of 10 with the harness.

The sample is too narrow for a general rule, but it is a useful warning against assuming that more feedback at every step always improves overall efficiency. [martinfowler.com](https://martinfowler.com/articles/are-harnesses-worth-the-cost.html?utm_source=chatgpt.com)

**Practical judgment:** retain independent final verification, then tune the frequency of intermediate checks to the task and model.

### Drew Breunig: specifications must evolve with implementation decisions

Breunig argues that specifications, tests, and code need continuing reconciliation. Implementation generates decisions that were absent from the original requirements; those decisions need to become visible rather than silently changing the product.

His Plumb experiment extracts decisions from diffs and agent traces around commits. It is an interesting approach to preserving intent, although it is explicitly experimental. [dbreunig.com](https://www.dbreunig.com/2026/03/04/the-spec-driven-development-triangle.html?utm_source=chatgpt.com)

The useful part is **reviewing consequential decisions**, especially where an agent invents behavior to resolve ambiguity. A spec that is automatically rewritten to agree with every implementation change loses its authority.

## 6. How to connect the north star to the ticket mechanically

The following is a proposed architecture, synthesized from the evidence and tool capabilities above.

### Keep the product goal compact and stable

The top-level charter should state:

- Who the product serves.
- Which user outcome matters.
- How that outcome will be measured.
- Important business invariants.
- Explicit non-goals.
- Which decisions require escalation.

Feature specifications then describe the behavior needed to advance that outcome.

The charter does not need to appear verbatim in every tool call. Each ticket needs the relevant portion and a reference to the authoritative version.

### Give each ticket a small, executable contract

For example:

| Field | Illustrative checkout ticket |
|---|---|
| **Goal connection** | Reduce checkout failures caused by transient network errors |
| **Authorized change** | Add retry handling to order submission |
| **Behavior** | Repeating the same request with the same idempotency key returns the original order |
| **Invariants** | No duplicate order or charge; no access across tenants |
| **Interface** | Accepted request/response schema and explicit error behavior |
| **Non-goals** | Changing pricing, replacing the payment provider, redesigning checkout |
| **Dependencies** | The idempotency contract must exist before parallel client/server implementation |
| **Acceptance evidence** | API tests, concurrent retry test, browser recovery scenario |
| **Escalation condition** | The agreed behavior requires an incompatible public interface or a new business decision |

This makes “stay focused” concrete. An unrelated refactor can be recorded as follow-up work without expanding the active ticket.

### Assemble context from authoritative artifacts

At the start of a task, provide:

1. The ticket and its acceptance criteria.
2. The relevant feature specification.
3. The applicable interfaces and invariants.
4. A small set of architecture decisions.
5. Relevant symbols, callers, and existing tests.
6. Known failures and the verification commands.

After a session reset, reconstruct those inputs from persistent state. Chat summaries remain useful, but they should not override the accepted ticket or current repository.

### Separate implementation authority from acceptance authority

The implementation agent needs freedom to repair its code. It should not be able to silently redefine success.

A practical division is:

- The agent can add developer tests and improve implementation.
- Accepted business expectations and public contracts have a distinct change path.
- CI executes the required checks against the actual resulting revision.
- Newly skipped tests and removed checks are surfaced.
- Changes to snapshots, expected outputs, or invariants receive explicit scrutiny.
- A ticket closes only after its required evidence exists and passes.

A Zod schema for a completion report can validate that the report contains fields. It cannot establish that the reported checks actually ran. Execution evidence must come from the runner.

Also, requirement IDs alone provide traceability. They do not prove that the linked test measures the requirement correctly.

### Make reviews produce actionable evidence

A useful reviewer instruction is:

> For each suspected functional regression, attempt to produce a minimal executable reproducer. Identify requirement ambiguity separately.

Meta's October 2026 JiTTesting account describes a related approach: generating tests that expose behavioral differences introduced by a proposed change, then filtering findings before escalation. This is company-reported deployment evidence, and the internal system is not established here as FOSS, but the method is transferable. [Engineering at Meta](https://engineering.fb.com/2026/10/29/security/catching-bugs-before-they-land-jittestings-human-on-the-loop-approach-at-full-scale/?utm_source=chatgpt.com)

A reproducible failure gives the implementation agent something concrete to fix. Review comments based solely on stylistic preference should carry less authority.

### Parallelize after the shared decisions exist

Before separate agents implement dependent components, establish the interface and failure semantics. Use isolated workspaces and designate one integration owner.

Re-run checks after integration. Individually passing branches do not establish that their combination works.

Keep retries bounded and diagnose repeated failures. An agent that repeatedly fails because the contract is contradictory needs a resolved decision; another unchanged attempt is unlikely to help.

Finally, product success still needs user or production feedback. Passing the checkout ticket's tests demonstrates the specified retry behavior. It does not establish that checkout abandonment decreased.

## 7. FOSS and maintenance details that change the shortlist

“Public GitHub repository” is not a sufficient FOSS check.

| Project | Current qualification |
|---|---|
| **GitNexus** | Uses PolyForm Noncommercial 1.0.0. Exclude it from an unrestricted FOSS shortlist. [GitHub](https://github.com/abhigyanpatwari/GitNexus/blob/main/LICENSE?utm_source=chatgpt.com) |
| **Task Master** | Uses MIT plus the Commons Clause, including restrictions on selling the software or certain services derived from it. It is not ordinary MIT/FOSS. [GitHub](https://github.com/eyaltoledano/claude-task-master/blob/main/LICENSE?utm_source=chatgpt.com) |
| **Context7** | Its MCP source is MIT, but its API backend, parsing engine, and crawling engine are private. Useful integration, but not a completely self-hostable FOSS documentation stack. [GitHub](https://github.com/upstash/context7?utm_source=chatgpt.com) |
| **Specmatic** | MIT core; several advanced protocols, workflow capabilities, and mocking features are commercial. Select features against the edition comparison. [Specmatic](https://docs.specmatic.io/references/open-source-vs-enterprise?utm_source=chatgpt.com) |
| **Serena** | Current application is GPL-3.0-or-later; SolidLSP remains MIT. [GitHub](https://github.com/oraios/serena/blob/main/LICENSE?utm_source=chatgpt.com) |

Open-source tooling also does not eliminate model inference or hosting costs. Tool licensing, model access, and runtime infrastructure are separate choices.

## 8. Recommended adoption order

For a TypeScript web product, this is the order most likely to produce useful evidence without introducing excessive process.

| Stage | Add or establish | Success criterion |
|---|---|---|
| **1. Intent and scope** | OpenSpec **or** Spec Kit; use existing tickets or Backlog.md | Fewer ambiguous requirements and fewer unrelated changes |
| **2. Shared contracts** | Explicit Zod/oRPC contracts; OpenAPI compatibility checks where relevant | Fewer frontend/backend disagreements and accidental breaking changes |
| **3. Behavioral verification** | Critical Playwright journeys; Schemathesis for APIs | More defects caught before review, with reproducible failures |
| **4. Test effectiveness** | fast-check and targeted Stryker runs | Important incorrect implementations are detected |
| **5. Focus and continuity** | Serena; Beads if dependency management warrants it | Less repeated exploration and fewer forgotten blockers |
| **6. Reviewable completion** | Showboat demonstrations and revision-bound CI evidence | Faster review with fewer unsupported completion claims |
| **7. Advanced reasoning and automation** | Quint for difficult stateful behavior; Symphony for ticket execution | More verified work completed with less human intervention |
| **8. Continuous evaluation** | Harbor with representative internal tasks | Retain only workflow additions that improve measured outcomes |

Track **accepted work per human hour**, total elapsed time, cost per accepted task, intervention count, and regressions. Separate task categories so that a collection of easy tickets does not appear to outperform a harder baseline.

Re-evaluate after changing models. METR's February 2026 update explicitly warned that its newer productivity estimates were unreliable because of selection and measurement problems; its earlier slowdown finding should not be treated as a timeless result. The same caution applies to claims that a particular harness always accelerates development. [METR](https://metr.org/blog/2026-02-24-uplift-update/?utm_source=chatgpt.com)

For the first trial, keep the existing coding agent and change only the surrounding workflow: **one accepted specification, one bounded ticket, explicit contracts, and independently executed acceptance checks**. Add each subsequent tool to address a failure that the trial actually exposes.

