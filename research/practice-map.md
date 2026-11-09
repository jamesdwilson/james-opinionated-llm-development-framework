# Research-to-practice map

This file separates standards, empirical findings, engineering reports, documented tool capabilities, and James's policy choices.

## Evidence labels

- **Standard:** consensus guidance and required information structures. Causal performance gains require separate empirical evidence.
- **Empirical:** observed or experimental results within a stated population and task.
- **Engineering report:** original operational experience from an uncontrolled setting.
- **Documented capability:** what a tool officially supports.
- **James's policy:** the playbook's chosen operating rule after weighing the available evidence.

## Project Brief and requirements

**Practice:** Keep one concise Project Brief covering purpose, outcomes, stakeholders, operational context, scope, observable behaviour, measurable quality requirements, constraints, assumptions, risks, open decisions, acceptance conditions, and verification links.

**Standards and research:** ISO/IEC/IEEE 29148 defines requirements-engineering processes and information items. [[21]](https://www.iso.org/standard/72089.html) NASA's systems-engineering handbook provides accessible guidance on stakeholder expectations, operational scenarios, well-formed requirements, and verification methods. [[30]](https://www.nasa.gov/wp-content/uploads/2018/09/nasa_systems_engineering_handbook_0.pdf) Goal-oriented requirements engineering connects strategic goals to technical requirements and preserves rationale. [[22]](https://webperso.info.ucl.ac.be/~avl/files/RE01.pdf) ISO/IEC 25010 supplies a quality model for specifying and evaluating consequential product qualities. [[29]](https://www.iso.org/standard/78176.html)

**Evidence boundary:** Research supports these contents and relationships. The compact Markdown file, filename, and section order are implementation choices. Optimal page count and a universal brief format remain open questions.

## Traceability and verification

**Practice:** Give each material requirement a stable ID, rationale or source, acceptance condition, and verification link. Verification may use tests, inspection, analysis, demonstration, or user validation.

**Evidence:** A controlled experiment found that requirements-to-code traceability improved maintenance-task speed and correctness for its participants and projects. [[23]](https://www.patrickmaeder.de/pdf/ICSM2012_maeder_egyed_AssessingEffectOfRequirementsTraceability.pdf) An industrial multi-case study examined how three companies use test cases as requirements and the communication challenges surrounding that practice. [[24]](https://doi.org/10.1016/j.infsof.2016.03.008) NASA's systems-engineering handbook documents distinct verification methods and validation against stakeholder expectations. [[30]](https://www.nasa.gov/wp-content/uploads/2018/09/nasa_systems_engineering_handbook_0.pdf)

**Evidence boundary:** The traceability experiment used students and two projects. The case study supplies industrial qualitative evidence. Stable IDs and compact tables are practical implementations of traceability. A universal format remains untested.

## Repository instructions

**Practice:** Keep `AGENTS.md` concise, local, and executable. Put indispensable commands, conventions, constraints, and links to authoritative project artefacts in predictable sections.

**Empirical evidence:** One 2026 study found generated context files reduced success in several settings and increased inference cost, while human-written files showed mixed benefits. [[1]](https://arxiv.org/abs/2602.11988) A separate study associated `AGENTS.md` with lower median runtime and output-token use, while semantic correctness remained outside its comprehensive evaluation. [[27]](https://arxiv.org/abs/2601.20404)

**James's policy:** Keep human-written instructions short and task-relevant. Use links to the Project Brief, journeys, tests, and acceptance contract. Skip generated repository tours.

## Discovery, clarification, and examples

**Practice:** Translate requirements into representative normal, boundary, failure, and recovery scenarios. Resolve consequential ambiguity before implementation.

**Evidence:** Example Mapping structures discovery as rules, examples, and open questions. [[3]](https://cucumber.io/docs/bdd/example-mapping/) TiCoder found that test-based interaction helped users evaluate generated code and reduced reported cognitive load in its study. [[25]](https://arxiv.org/abs/2404.10100) ClarifyGPT improved code-generation results in its studied benchmark by detecting ambiguous interpretations and asking targeted questions. [[26]](https://arxiv.org/abs/2310.10996)

**Evidence boundary:** The empirical studies used relatively small programming tasks and participant groups. They support clarification and concrete examples. Optimal scenario count and syntax remain open questions.

## Structure as specification

**Practice:** Use obvious entry points, one source of truth per contract, explicit interfaces, product-language names, short dependency paths, and local invariants.

**Evidence:** Skeleton Coding reports that code-like structural specifications can outperform behavioural prose alone in its studied generation settings. [[4]](https://arxiv.org/abs/2610.38214)

**Evidence boundary:** The work is a recent preprint using specifications derived from reference implementations. It supports selective structural contracts and leaves broad architecture prescription unjustified.

## Test-guided implementation

**Practice:** Begin a behaviour change with a failing check. Use relevant representative tests and execution feedback. Keep the accepted test inventory independently reviewable.

**Evidence:** TDDev reports stronger functional accuracy from test-driven multi-agent iterations. [[5]](https://arxiv.org/abs/2605.17242) TestSuiteBench shows that coding agents struggle to generate strong repository-level suites from specifications. [[6]](https://arxiv.org/abs/2610.13065) TENET reports gains from representative developer-written tests, test-guided retrieval, and iterative failure analysis; moderate diverse subsets sometimes outperformed larger sets. [[28]](https://arxiv.org/abs/2509.24148)

**Evidence boundary:** TENET studies existing tests and stops short of evaluating the complete RED, GREEN, REFACTOR cycle. Full-cycle TDD remains the playbook's policy, supported by related evidence; a universal causal result remains unestablished.

## Deterministic browser authority

**Practice:** Use browser tests for visible journeys, permissions, reloads, state, provenance, recovery, and cleanup. Use user-visible locators and isolated tests.

**Documented capability:** Playwright's best-practices guide recommends user-facing assertions, resilient locators, isolation, and web-first waiting. [[7]](https://playwright.dev/docs/best-practices)

## Bounded model review

**Practice:** Give model review a short visible-UX brief and a strict result schema. Use an isolated negative control. Let deterministic evidence control acceptance.

**Documented capability:** Midscene provides AI-assisted interaction and assertion through Playwright. [[10]](https://midscenejs.com/integrate-with-playwright.html)

**James's policy:** Confine that capability to short questions about visible clarity and friction. Empirical support for this exact negative-control pattern remains absent.

## Failure and recovery

**Practice:** Inject controlled boundary failures, record the expected stop point, preserve user state as specified, and prove cleanup.

**Documented capability:** Bugsink offers a self-hosted Sentry-compatible target. [[11]](https://www.bugsink.com/docs/)

**James's policy:** Use a disposable instance or isolated project for synthetic error exercises.

## Supply-chain controls

**Practice:** Pin, hash, quarantine, audit, assess reachability, and keep a rollback path.

**Standards and documented capabilities:** Bun exposes `minimumReleaseAge` and a native audit command. [[12]](https://bun.com/docs/pm/cli/audit) [[13]](https://bun.com/docs/runtime/bunfig) NIST SSDF places secure practice throughout development. SLSA provenance links artefacts to their build context. [[14]](https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-218.pdf) [[15]](https://slsa.dev/spec/v1.2/provenance)

## Harness size

**Practice:** Carry a harness component when it turns a named uncertainty into repeatable evidence and justifies its maintenance cost.

**Engineering analysis:** Fowler frames harness adoption as a cost-benefit choice. METR's 2026 update documents selection effects and time-measurement problems that made its newer productivity experiment unreliable for estimating current impact. [[18]](https://martinfowler.com/articles/are-harnesses-worth-the-cost.html) [[19]](https://metr.org/blog/2026-02-24-uplift-update)

## Long-running agent work

**Practice:** Keep the repository legible, enforce invariants mechanically, record durable progress, run tests, and leave useful handoffs.

**Engineering reports:** OpenAI's harness engineering and Anthropic's long-running-agent guidance converge on these operational practices. [[16]](https://openai.com/index/harness-engineering) [[17]](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)

## Reusable agent workflows

**Practice:** Create a repository skill after a workflow repeats. Keep its trigger clear, instructions compact, and deterministic scripts linked from the main file.

**Documented capability:** OpenAI's Codex skill guidance recommends focused `SKILL.md` files with supporting references and scripts loaded only when needed. [[20]](https://developers.openai.com/codex/skills/)
