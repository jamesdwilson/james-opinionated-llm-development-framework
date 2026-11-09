# James's Opinionated LLM Development Playbook

> Give the agent room to work. Keep proof mechanical.

This repository contains reusable instructions, templates, and checks for LLM-assisted software delivery. Point a coding agent here, choose a profile, and let it adapt the method to your project.

The aim is simple: faster implementation, fewer plausible mistakes, and evidence you can inspect without trusting a victory speech from the same model that wrote the code.

The playbook gets there by:

- **Briefing the agent properly.** It receives the product promise, repository rules, exact commands, decision boundaries, and definition of done.
- **Turning intent into executable examples.** Rules and user journeys are written before the agent starts shaping the implementation.
- **Giving every claim an authority.** Fast tests prove logic and contracts. Real browser journeys prove user-facing behaviour. Model review handles short questions about clarity and friction.
- **Binding results to the exact candidate.** Commands, reports, runtime identity, and evidence stay attached to the code under review.
- **Finishing with a fresh challenge.** An independent reviewer hunts for weak tests, stale evidence, permissive parsers, and plausible stories unsupported by the results.

These recommendations draw on extensive work by researchers, standards bodies, tool maintainers, and engineering teams. The evidence covers repository instructions and test-driven agents [[1]](https://arxiv.org/abs/2602.11988) [[5]](https://arxiv.org/abs/2605.17242) [[6]](https://arxiv.org/abs/2610.13065), browser testing and software supply-chain practice [[7]](https://playwright.dev/docs/best-practices) [[14]](https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-218.pdf) [[15]](https://slsa.dev/spec/v1.2/provenance), and the engineering realities of long-running agents and measured developer productivity [[16]](https://openai.com/index/harness-engineering) [[17]](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) [[19]](https://metr.org/blog/2026-02-24-uplift-update).

The playbook turns that research into defaults an agent can execute. Every major recommendation links to its source, and [`research/practice-map.md`](research/practice-map.md) records how the evidence became a practical rule.

## Start here

Give your coding agent this prompt:

```text
Read https://github.com/jamesdwilson/james-opinionated-llm-development-framework

Start with ADOPT.md, then read AGENTS.md and the profile files.
Apply the Standard profile to this repository.
Preserve the healthy parts of the existing stack.
Create only the missing project instructions, product promise, journey catalogue,
acceptance contract, tests, and evidence records.
Use deterministic checks as release authority.
Use model judgement only for bounded questions that require human-like perception.
Run the resulting checks and leave a concise handoff with commands, results,
changed files, remaining risks, and the next concrete action.
```

Replace `Standard` with `Lean` for a small prototype or `High Assurance` for costly, sensitive, or difficult-to-reverse work.

The full adoption contract lives in [`ADOPT.md`](ADOPT.md). A ready-to-copy project instruction file lives in [`templates/AGENTS.md`](templates/AGENTS.md).

Standard is the default for a maintained repository. A direct request for Lean or High Assurance controls the choice. The agent can recommend a change after inspecting the project and explaining the main risk.

## What the playbook gives you

- a short repository instruction file for coding agents;
- a versioned product promise;
- examples and journeys before implementation;
- an explicit acceptance hierarchy;
- deterministic unit, integration, contract, and browser checks;
- bounded model review for questions about clarity and friction;
- failure and recovery exercises;
- dependency pinning, quarantine, and audit guidance;
- candidate and evidence records for higher-risk releases;
- an independent adversarial review brief;
- three profiles that keep the method proportional to the work.

The templates fit any language or framework. The suggested tools favour a small JavaScript or TypeScript stack because they offer a strong default with little plumbing.

The playbook uses a short `AGENTS.md` as its entry point. Research on repository instructions found that context quality matters more than context volume, with generated instructions sometimes increasing cost and reducing success. [[1]](https://arxiv.org/abs/2602.11988) The open `AGENTS.md` format gives agents a predictable place for commands, conventions, and boundaries. [[2]](https://agents.md/)

## Choose the smallest useful profile

### Lean

Use for prototypes, internal tools, and reversible changes.

- concise `AGENTS.md`;
- North Star;
- representative journeys;
- native unit and integration tests;
- one browser journey for a user-facing product;
- pinned dependencies and the native audit command;
- short evidence handoff.

See [`profiles/lean.md`](profiles/lean.md).

### Standard

Use for maintained products and most production work.

Everything in Lean, plus:

- acceptance matrix;
- RED, GREEN, REFACTOR discipline;
- browser coverage for critical journeys;
- deliberate failure and recovery checks;
- bounded model review where deterministic checks cannot answer the question;
- reviewed evidence from the exact candidate;
- fresh independent review before release.

See [`profiles/standard.md`](profiles/standard.md).

### High Assurance

Use when failure carries material financial, privacy, security, legal, or operational cost.

Everything in Standard, plus:

- exact candidate fingerprint;
- hashed evidence manifest;
- repeated clean runs;
- fail-closed parsers and closure checks;
- isolated observability exercises;
- forced failures and cleanup proof;
- read-only hostile review of implementation and acceptance machinery.

See [`profiles/high-assurance.md`](profiles/high-assurance.md).

Use Standard for general adoption. Lean suits explicitly reversible prototypes. High Assurance suits the triggers listed in its profile.

## The method

### 1. Write the product promise

Capture the user, job, desired experience, decision boundaries, and success signals in one page. Keep product language separate from implementation language.

Use [`templates/NORTH_STAR.md`](templates/NORTH_STAR.md).

### 2. Turn promises into rules, examples, and questions

Example Mapping keeps discovery concrete: one story, a small set of rules, examples beneath each rule, and questions where the team still lacks an answer. [[3]](https://cucumber.io/docs/bdd/example-mapping/)

For each important journey, record:

- starting state;
- user action;
- visible outcome;
- stored outcome;
- permission boundary;
- recovery path;
- provenance requirement;
- open question.

Use [`templates/JOURNEYS.md`](templates/JOURNEYS.md).

### 3. Shape the smallest coherent slice

Build one end-to-end slice with real inputs, real persistence where the product needs it, and a visible result. Program structure can act as a specification for coding agents, reducing ambiguity before test execution begins. [[4]](https://arxiv.org/abs/2610.38214)

Good structure for agents is easy to inspect:

- obvious entry points;
- one source of truth for each contract;
- names that match product language;
- short dependency paths;
- explicit boundaries;
- small files with clear ownership.

Add an abstraction on its second real use. Add a dependency when it removes more complexity than it introduces.

### 4. Write the counterexample first

A behaviour change begins with a failing test. A behaviour-preserving adoption task may begin with a focused characterisation or structural verification. The implementation then earns GREEN with the smallest coherent change, followed by cleanup.

Recent full-stack agent research reports stronger functional accuracy from test-driven iterations than from one-pass implementation. [[5]](https://arxiv.org/abs/2605.17242) TestSuiteBench also shows that coding agents still struggle to create strong repository-level test suites from specifications, so the test inventory deserves independent review. [[6]](https://arxiv.org/abs/2610.13065)

The working loop is:

```text
promise -> example -> failing check -> small change -> green check -> cleanup
```

### 5. Give each test layer one job

Use the fastest deterministic layer that can prove the claim.

- **Unit tests** own pure rules and transformations.
- **Integration tests** own persistence, services, queues, and adapters.
- **Contract tests** own schemas, status codes, compatibility, and boundary behaviour.
- **Browser tests** own visible user journeys, reloads, permissions, and client-side recovery.
- **Model review** answers bounded questions about clarity, hierarchy, ambiguity, and friction.

Playwright recommends user-visible assertions, isolated tests, resilient locators, and web-first waiting. [[7]](https://playwright.dev/docs/best-practices) Bun offers a built-in test runner for a compact JavaScript or TypeScript setup. [[8]](https://bun.com/docs/test)

Keep a healthy existing test stack. Apply the authority split with the tools already present.

### 6. Use browser tests as product evidence

A browser check exercises the journey's actions and resulting state.

A useful journey proves:

1. the required state can be created;
2. the user can discover the next action;
3. permissions behave as promised;
4. data survives reload where persistence matters;
5. errors preserve work and expose recovery;
6. history and actor identity remain accurate;
7. cleanup leaves the test environment reusable.

Use native semantic HTML, labels, roles, visible names, and a small number of stable test IDs. These improve human usability, browser locators, and agent visibility at the same time.

Playwright's planner, generator, and healer agents can assist test creation. Release authority stays with the deterministic test result and reviewed journey contract. [[9]](https://playwright.dev/docs/test-agents)

### 7. Give model judgement a narrow brief

Model review adds value when the question requires perception:

- Is this required choice understandable?
- Is the next action obvious?
- Does the interface explain who must act?
- Can a user recover after a visible failure?
- Does the completed state match the journey promise?

Midscene integrates AI-assisted interaction and assertion with Playwright and can produce review reports. [[10]](https://midscenejs.com/integrate-with-playwright.html)

Use a structured result:

```json
{
  "verdict": "GREEN | RED | UNCLEAR",
  "stopped_at": "short stable label",
  "evidence": ["visible fact"],
  "reason": "one concise explanation"
}
```

`RED` or `UNCLEAR` on a required product journey stops acceptance. `GREEN` enters the evidence set after deterministic checks pass on the same candidate.

A negative control keeps the reviewer honest. Give it one deliberately ambiguous journey with an expected RED result. That RED passes the calibration check. `GREEN` or `UNCLEAR` fails calibration.

### 8. Exercise failure and recovery

Success-path coverage leaves the fragile parts untouched. Add controlled failures at the boundaries your product depends on:

- startup;
- database or API access;
- authentication and permissions;
- callbacks and child processes;
- timeouts and oversized responses;
- browser reloads;
- partial writes;
- cleanup.

Each exercise records the expected failure point, visible behaviour, retained state, recovery action, and cleanup result.

For error tracking, use synthetic data and an isolated project or disposable service. Bugsink provides a self-hosted Sentry-compatible error tracking target for this kind of exercise. [[11]](https://www.bugsink.com/docs/)

### 9. Keep supply-chain work predictable

Pin direct dependencies. Commit the lockfile. Review graph changes. Use the package manager's audit command. Delay newly published packages when the ecosystem supports quarantine.

Bun's `minimumReleaseAge` setting can hold back packages published within a chosen window, while `bun audit` checks the installed dependency tree against vulnerability data. [[12]](https://bun.com/docs/pm/cli/audit) [[13]](https://bun.com/docs/runtime/bunfig)

A useful dependency decision records:

- the gap the package closes;
- exact version;
- release age;
- advisory status;
- transitive graph change;
- reachable risk;
- available fixed version;
- rollback path.

NIST's Secure Software Development Framework recommends integrating secure practices throughout development. [[14]](https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-218.pdf) SLSA provenance guidance adds a practical model for linking an artefact to where, when, and how it was produced. [[15]](https://slsa.dev/spec/v1.2/provenance)

### 10. Bind evidence to the candidate

A green result has value when it belongs to the bytes under review.

The Standard profile records:

- a verified clean commit or a working-tree identity;
- exact command;
- start and end time;
- exit code;
- test counts;
- report path;
- changed files;
- environment facts that affect execution.

For a clean candidate, record the commit and verify that the working tree contains no relevant changes. For a dirty candidate, fingerprint the fully materialised relevant tree. Include each path, file state, type, executable mode, bytes or symlink target, plus a deletion marker for each relevant base path now absent. Sort records by path and use unambiguous length-prefixed fields. Keep generated reports and evidence outputs outside the candidate input set.

The High Assurance profile adds hashes for source inputs, lockfiles, runtime versions, browser binaries, reports, and evidence manifests.

The closure rule is straightforward:

```text
same candidate + complete accepted checks + intact evidence + independent review
```

For the same candidate and required check, the latest completed attempt controls the result. An expected RED from an isolated negative control passes that control. A repaired failure remains in history while the changed candidate receives a fresh acceptance run. Missing, malformed, stale, or ambiguous evidence stops closure.

Use [`templates/EVIDENCE.md`](templates/EVIDENCE.md).

### 11. Run a fresh adversarial review

A fresh reviewer receives read-only access and an explicit hostile brief. Its job is to find a counterexample, a bypass, stale evidence, a permissive parser, a weak test, or an unjustified claim.

OpenAI's harness work emphasises repository legibility, enforceable invariants, and fast feedback loops as agent autonomy grows. [[16]](https://openai.com/index/harness-engineering) Anthropic's long-running-agent guidance emphasises durable progress records, incremental work, tests, and useful handoffs. [[17]](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)

Use [`templates/ADVERSARIAL_REVIEW.md`](templates/ADVERSARIAL_REVIEW.md).

### 12. Leave a handoff another person can run

A useful handoff contains:

- outcome;
- changed files;
- commands executed;
- exact results;
- evidence locations;
- known risks;
- remaining work;
- one next action.

A polished summary ranks last in the evidence hierarchy. Keep it short and make every claim traceable.

## Evidence hierarchy

Every applicable required check must pass. When two pieces of evidence address the same claim, use this order:

1. security and permission checks;
2. domain, persistence, and API checks;
3. deterministic browser journeys;
4. failure, recovery, and cleanup evidence;
5. dependency and provenance checks;
6. bounded model judgement;
7. prose summaries.

The higher-ranked evidence controls that shared claim. Any required failure blocks acceptance.

## Recommended tool split

| Need | Default | Role |
|---|---|---|
| JavaScript runtime and fast tests | Bun | deterministic unit and integration checks |
| Browser journeys | Playwright | deterministic visible behaviour |
| Visible UX judgement | Midscene | bounded model review |
| Error capture exercise | Bugsink or an isolated project in your existing tracker | synthetic canary and recovery proof |
| Supply-chain check | native package-manager audit | resolved dependency review |
| Candidate identity | Git plus hashes | bind evidence to exact inputs |
| Final challenge | fresh agent, model, or human reviewer | hostile review |

Keep existing tools when they cover the same roles. The method travels through its authority boundaries and evidence contracts.

## Rules that keep the playbook lean

- Use the selected profile and its applicability rules.
- Keep one runtime where the project allows it.
- Give each tool one job.
- Share one contract across implementation, tests, and documentation.
- Prefer native semantics and stable names.
- Add abstraction on its second real use.
- Add a dependency after naming the gap it closes.
- Keep agent instructions short, local, and executable.
- Preserve raw evidence separately from summaries.
- Re-run acceptance after any candidate change.

Harness work has value when it turns a named uncertainty into repeatable evidence. Fowler's analysis offers a useful test: carry the infrastructure when the saved effort and reduced risk justify its maintenance cost. [[18]](https://martinfowler.com/articles/are-harnesses-worth-the-cost.html) METR's 2026 update shows why productivity claims need careful study design: selection effects and time-measurement problems made its newer experiment unreliable for estimating current impact. [[19]](https://metr.org/blog/2026-02-24-uplift-update)

## Repository map

- [`ADOPT.md`](ADOPT.md) - agent-facing adoption contract.
- [`AGENTS.md`](AGENTS.md) - instructions for agents working with this playbook.
- [`profiles/`](profiles/) - Lean, Standard, and High Assurance scopes.
- [`templates/`](templates/) - ready-to-copy project artefacts.
- [`checklists/release.md`](checklists/release.md) - release evidence checklist.
- [`examples/standard-adoption.md`](examples/standard-adoption.md) - a compact worked adoption.
- [`research/practice-map.md`](research/practice-map.md) - recommendation-to-source map.
- [`research/sources.json`](research/sources.json) - machine-readable citation ledger.
- [`tools/verify_playbook.py`](tools/verify_playbook.py) - citation, link, and prose guardrails.

## Maintaining the playbook

Run the zero-dependency verifier after editing prose or sources:

```bash
python3 tools/verify_playbook.py
```

It checks citation and ledger structure, local Markdown links, and the main adoption copy's prose guardrails. Source review remains a separate editorial task.

## A note on repository skills

Coding-agent skills work best as narrow workflows with a clear trigger, compact instructions, deterministic scripts where useful, and explicit output. OpenAI's skill guidance recommends keeping `SKILL.md` focused and moving reference material or scripts into linked files. [[20]](https://developers.openai.com/codex/skills/)

This playbook starts with `AGENTS.md` because it is portable across coding agents. A project-specific skill becomes worthwhile when the same workflow repeats often enough to deserve its own trigger and script.

## Sources

- [[1]](https://arxiv.org/abs/2602.11988) *Evaluating AGENTS.md: Are Repository-Level Context Files Helpful for Coding Agents?*
- [[2]](https://agents.md/) AGENTS.md open format
- [[3]](https://cucumber.io/docs/bdd/example-mapping/) Cucumber Example Mapping
- [[4]](https://arxiv.org/abs/2610.38214) *Skeleton Coding: Program Structure as a Specification for Agents*
- [[5]](https://arxiv.org/abs/2605.17242) *From Runnable to Shippable: Multi-Agent Test-Driven Development for Generating Full-Stack Web Applications from Requirements*
- [[6]](https://arxiv.org/abs/2610.13065) *TestSuiteBench: Coding Agents Struggle to Generate Strong Test Suites from Specifications*
- [[7]](https://playwright.dev/docs/best-practices) Playwright Best Practices
- [[8]](https://bun.com/docs/test) Bun Test Runner
- [[9]](https://playwright.dev/docs/test-agents) Playwright Test Agents
- [[10]](https://midscenejs.com/integrate-with-playwright.html) Midscene Playwright Integration
- [[11]](https://www.bugsink.com/docs/) Bugsink Documentation
- [[12]](https://bun.com/docs/pm/cli/audit) Bun Audit
- [[13]](https://bun.com/docs/runtime/bunfig) Bun Configuration
- [[14]](https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-218.pdf) NIST Secure Software Development Framework
- [[15]](https://slsa.dev/spec/v1.2/provenance) SLSA Provenance
- [[16]](https://openai.com/index/harness-engineering) OpenAI Harness Engineering
- [[17]](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) Anthropic Effective Harnesses for Long-Running Agents
- [[18]](https://martinfowler.com/articles/are-harnesses-worth-the-cost.html) Martin Fowler, *Are Harnesses Worth the Cost?*
- [[19]](https://metr.org/blog/2026-02-24-uplift-update) METR, *We are Changing our Developer Productivity Experiment Design*
- [[20]](https://developers.openai.com/codex/skills/) OpenAI Codex Skills

## Status

This is an opinionated playbook. Treat it as a strong starting point, then keep the parts that earn their place in your repository.
