# Research-to-practice map

This file explains how the sources changed the playbook. The README carries the full method and clickable citations.

## Repository instructions

**Practice:** Keep `AGENTS.md` concise, local, and executable. Put build commands, tests, conventions, and safety boundaries in predictable sections.

**Evidence:** The open AGENTS.md format defines the portable convention. A 2026 evaluation found that generated context files could increase inference cost and reduce task success, which supports disciplined instruction size and content. [[1]](https://arxiv.org/abs/2602.11988) [[2]](https://agents.md/)

## Discovery through examples

**Practice:** Express each important behaviour as rules, examples, and open questions before implementation.

**Evidence:** Cucumber's Example Mapping method uses that exact structure to build shared understanding before development. [[3]](https://cucumber.io/docs/bdd/example-mapping/)

## Structure as specification

**Practice:** Choose obvious entry points, one source of truth per contract, product-language names, and short dependency paths.

**Evidence:** Skeleton Coding reports that program structure can serve as a specification for agents and reduce reliance on tests alone. [[4]](https://arxiv.org/abs/2610.38214)

## Test-driven implementation

**Practice:** Begin behaviour changes with a failing check, implement a small coherent slice, then clean up.

**Evidence:** TDDev reports stronger functional accuracy from test-driven multi-agent iterations. TestSuiteBench shows the remaining weakness: coding agents struggle to generate strong repository-level suites from specifications. [[5]](https://arxiv.org/abs/2605.17242) [[6]](https://arxiv.org/abs/2610.13065)

## Deterministic browser authority

**Practice:** Use browser tests for visible journeys, permissions, reloads, state, provenance, recovery, and cleanup. Use user-visible locators and isolated tests.

**Evidence:** Playwright's best-practices guide recommends user-facing assertions, resilient locators, isolation, and web-first waiting. [[7]](https://playwright.dev/docs/best-practices)

## Bounded model review

**Practice:** Give model review a short visible-UX brief and a strict result schema. Use a negative control. Let deterministic evidence control acceptance.

**Documented capability:** Midscene provides AI-assisted interaction and assertion through Playwright. James's policy confines that capability to short questions about visible clarity and friction, with deterministic checks controlling acceptance. [[10]](https://midscenejs.com/integrate-with-playwright.html)

## Failure and recovery

**Practice:** Inject controlled boundary failures, record the expected stop point, preserve user state as specified, and prove cleanup.

**Documented capability:** Bugsink offers a self-hosted Sentry-compatible target. James's policy uses a disposable instance or isolated project for synthetic error exercises. [[11]](https://www.bugsink.com/docs/)

## Supply-chain controls

**Practice:** Pin, hash, quarantine, audit, assess reachability, and keep a rollback path.

**Evidence:** Bun exposes `minimumReleaseAge` and a native audit command. NIST SSDF places secure practice throughout development. SLSA provenance links artefacts to their build context. [[12]](https://bun.com/docs/pm/cli/audit) [[13]](https://bun.com/docs/runtime/bunfig) [[14]](https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-218.pdf) [[15]](https://slsa.dev/spec/v1.2/provenance)

## Harness size

**Practice:** Carry a harness component when it turns a named uncertainty into repeatable evidence and justifies its maintenance cost.

**Evidence:** Fowler frames harness adoption as a cost-benefit choice. METR's 2026 update documents selection effects and time-measurement problems that made its newer productivity experiment unreliable for estimating current impact. [[18]](https://martinfowler.com/articles/are-harnesses-worth-the-cost.html) [[19]](https://metr.org/blog/2026-02-24-uplift-update)

## Long-running agent work

**Practice:** Keep the repository legible, enforce invariants mechanically, record durable progress, run tests, and leave useful handoffs.

**Evidence:** OpenAI's harness engineering and Anthropic's long-running-agent guidance converge on these operational practices. [[16]](https://openai.com/index/harness-engineering) [[17]](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)

## Reusable agent workflows

**Practice:** Create a repository skill after a workflow repeats. Keep its trigger clear, instructions compact, and deterministic scripts linked from the main file.

**Evidence:** OpenAI's Codex skill guidance recommends focused `SKILL.md` files with supporting references and scripts loaded only when needed. [[20]](https://developers.openai.com/codex/skills/)
