# Research-to-practice map

This file separates authorities, empirical findings, tool capabilities, engineering reports, and James's stack choices.

## Evidence labels

- **Standard or handbook:** consensus processes, information categories, or established engineering guidance within scope.
- **Empirical:** observed or experimental results limited to the study's population, tasks, systems, measures, and design.
- **Documented capability:** what a tool's maintainer says it supports.
- **Engineering report:** operational experience from an uncontrolled setting.
- **James's stack choice:** the selected way these components work together.

## Project Brief

**Practice:** Record purpose, stakeholders, context, scope, requirements, quality attributes, constraints, rationale, assumptions, risks, decisions, acceptance conditions, and evidence links.

**Support:** ISO/IEC/IEEE 29148 covers requirements-engineering processes and information items. [[1]](https://www.iso.org/standard/72089.html) NASA covers stakeholder expectations, operational concepts, requirements, verification, and validation. [[2]](https://www.nasa.gov/wp-content/uploads/2018/09/nasa_systems_engineering_handbook_0.pdf) ISO/IEC 25010 supplies a product-quality model. [[3]](https://www.iso.org/standard/78176.html) Goal-oriented requirements engineering connects goals, requirements, and rationale. [[4]](https://webperso.info.ucl.ac.be/~avl/files/RE01.pdf)

**Boundary:** The sources support the information and relationships. The Markdown filename and layout are packaging choices.

## BDD discovery

**Practice:** Use rules, examples, and questions to clarify requirements and representative scenarios.

**Support:** Example Mapping is the selected practitioner technique. [[13]](https://cucumber.io/docs/bdd/example-mapping/) NASA uses operational concepts and scenarios to describe expected use. [[2]](https://www.nasa.gov/wp-content/uploads/2018/09/nasa_systems_engineering_handbook_0.pdf) TiCoder and ClarifyGPT support concrete tests and targeted clarification in their evaluated settings. [[7]](https://arxiv.org/abs/2404.10100) [[8]](https://arxiv.org/abs/2310.10996)

**Boundary:** The exact BDD syntax, scenario count, and sequencing are James's stack choices.

## TDD and test strength

**Practice:** Use RED, GREEN, REFACTOR for changed behaviour, then run affected broader checks.

**Empirical evidence:** Across 20 diverse web applications, TDDev reports accuracy gains of 15.5 to 23.7 percentage points with sufficiently capable backbones; a stronger tester restored positive gains for a lower-capability backbone. [[15]](https://arxiv.org/abs/2605.17242) TENET reports benefits from representative developer-written tests, test-guided retrieval, and iterative failure analysis. [[12]](https://arxiv.org/abs/2509.24148) TestSuiteBench reports difficulty generating strong repository-level suites from specifications. [[11]](https://arxiv.org/abs/2610.13065)

**Boundary:** Full RED, GREEN, REFACTOR and the exact layer split are James's stack choices. The studies support conditional test-guided repair and do not establish universal benefit or one superior sequence.

## Structure as specification

**Practice:** Keep entry points, interfaces, invariants, and ownership easy for agents to inspect.

**Empirical evidence:** Skeleton Coding reports benefits from structural specifications in its evaluated generation settings. [[14]](https://arxiv.org/abs/2610.38214)

**Boundary:** The study does not justify a universal architecture or file-size rule.

## Bun

**Role:** Default JavaScript or TypeScript runtime, package manager, and test runner.

**Documented capabilities:** Bun supplies a built-in test runner, dependency audit command, and minimum release-age configuration. [[18]](https://bun.com/docs/test) [[21]](https://bun.com/docs/pm/cli/audit) [[22]](https://bun.com/docs/runtime/bunfig)

**Boundary:** Selecting Bun is James's stack choice. The documentation does not establish superiority over a healthy existing runtime.

## Playwright

**Role:** Deterministic rendered journeys and browser state.

**Maintainer guidance:** Playwright recommends isolated tests, user-facing assertions, resilient locators, and web-first waiting. [[16]](https://playwright.dev/docs/best-practices) Its test agents can assist test creation. [[17]](https://playwright.dev/docs/test-agents)

**Boundary:** Playwright is the stack default. The sources do not prove universal defect-detection superiority or freedom from flakiness.

## Midscene

**Role:** Bounded AI-assisted observations about visible clarity and friction.

**Documented capability:** Midscene integrates AI-assisted interaction and assertions with Playwright. [[19]](https://midscenejs.com/integrate-with-playwright.html)

**Boundary:** Documentation establishes capability, not agreement with representative users. Midscene remains advisory until the target project validates its model, prompt, fixtures, and human agreement.

## Diagnostics and recovery

**Role:** Isolated synthetic error capture and recovery exercise.

**Documented capability:** Bugsink provides a self-hosted Sentry-compatible error tracking target. [[20]](https://www.bugsink.com/docs/)

**Boundary:** Bugsink is a historical example, not the new-install default. Telemetry and hosting selection are parked; [DIAGNOSTICS.md](../DIAGNOSTICS.md) preserves the research without activation authority. Native failure/recovery checks remain independent. No empirical claim of superior agent productivity is established. The affected product requirement chooses the failure, expected user behaviour, recovery and data boundary.

## Supply chain

**Practice:** Inspect the resolved dependency graph, run available advisory checks, apply the project's package-admission policy, and keep rollback available.

**Support:** Bun documents audit and release-age controls. [[21]](https://bun.com/docs/pm/cli/audit) [[22]](https://bun.com/docs/runtime/bunfig) [[27]](https://bun.com/docs/pm/cli/install) NIST SSDF supplies broader secure-development guidance. [[23]](https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-218.pdf)

**Boundary:** The playbook sets no universal release-age duration and makes no claim that advisory databases detect every malicious package. The release-age filter applies during new resolution, not retroactively to existing lockfile entries. An audit may skip a scoped registry without an advisory endpoint while retaining a successful exit code.

## Traceability, provenance, and evidence

**Practice:** Connect requirements, journeys, procedures, results, evidence, and limits to the project-native revision or artefact identity.

**Support:** A controlled traceability experiment found maintenance benefits for its participants and projects. [[5]](https://www.patrickmaeder.de/pdf/ICSM2012_maeder_egyed_AssessingEffectOfRequirementsTraceability.pdf) An industrial multi-case study documents the use and communication limits of tests as requirements. [[6]](https://doi.org/10.1016/j.infsof.2016.03.008) SLSA supplies a provenance model for linking artefacts to build context. [[24]](https://slsa.dev/spec/v1.2/provenance)

**Boundary:** The playbook does not claim SLSA compliance or define a custom cryptographic identity protocol.

## Repository instructions and handoff

**Practice:** Connect the stack to real project paths and commands through a concise `AGENTS.md`, then leave durable results and limits.

**Evidence and reports:** Repository-instruction studies report mixed outcomes and efficiency findings. The generated-context study's aggregate success differences were not statistically significant. [[9]](https://arxiv.org/abs/2602.11988) [[10]](https://arxiv.org/abs/2601.20404) OpenAI and Anthropic engineering reports emphasise repository legibility, mechanical checks, durable progress, and handoffs. [[25]](https://openai.com/index/harness-engineering) [[26]](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)

**Boundary:** The exact template, length, reviewer, and handoff format are James's stack choices or target-project decisions.
