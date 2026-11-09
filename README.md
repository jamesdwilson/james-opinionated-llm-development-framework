# James's Research-Led LLM Development Playbook

> A small set of project facts, examples, and verification links that any coding agent can use.

This repository gives a coding agent enough reliable context to work in an existing codebase without importing a new development religion. It keeps the project's tools, architecture, security rules, and release process in charge.

The playbook asks for three things:

1. a concise description of the problem, stakeholders, requirements, and constraints;
2. representative scenarios that reveal ambiguity and support clarification;
3. a verification and validation record connecting each important claim to suitable evidence.

That is the whole method.

## Why use it

- **Easy to adopt.** Reuse existing documents and add only the missing information, using the templates where helpful.
- **Portable.** It prescribes no runtime, framework, test runner, browser tool, model, or release process.
- **Traceable.** Requirements connect to scenarios, verification methods, results, and known limits.
- **Research-led.** Standards and empirical studies support the contents. The repository avoids numerical thresholds and universal workflow claims that the evidence does not establish.
- **Honest about authority.** The source responsible for each claim stays visible.

## Core rule

Use the authority appropriate to the claim.

- Stakeholders and product requirements define the intended outcome.
- Applicable laws, standards, policies, and contracts define mandatory constraints.
- Authoritative schemas, interfaces, and source code define existing technical behaviour.
- Testing, inspection, analysis, and demonstration provide verification evidence.
- Validation checks intended use and stakeholder expectations.
- Research informs process choices within the populations, tasks, and limits that were actually studied.

When sources conflict or leave a consequential gap, record the conflict and resolve it with the responsible person or authority. Do not turn an unsupported preference into a universal rule.

## Start here

Give your coding agent this prompt:

```text
Read https://github.com/jamesdwilson/james-opinionated-llm-development-framework

Read this playbook's ADOPT.md.
In the target repository, read its own instructions and inspect it before changing it.
Do not apply this playbook's root AGENTS.md to the target repository.
Follow the target repository's documented tools, conventions, authorities, and release process.
Create or update only the Project Brief, representative journeys, and
verification and validation record that the work needs.
Identify consequential ambiguity and seek targeted clarification or record the responsible assumption.
Connect each material requirement to suitable verification or validation evidence.
Run the relevant existing checks and report the results, limits, and unresolved risks.
```

The detailed adoption instructions live in [`ADOPT.md`](ADOPT.md).

## The minimal set

### 1. Project Brief

Record:

- purpose and desired outcomes;
- stakeholders and operational context;
- included and excluded scope;
- observable requirements;
- measurable quality requirements where they matter;
- genuine constraints and their authority;
- assumptions, risks, and unresolved decisions;
- acceptance conditions and verification or validation links.

ISO/IEC/IEEE 29148 defines requirements-engineering processes and information items. [[1]](https://www.iso.org/standard/72089.html) NASA's Systems Engineering Handbook covers stakeholder expectations, operational concepts, requirements, verification, and validation. [[2]](https://www.nasa.gov/wp-content/uploads/2018/09/nasa_systems_engineering_handbook_0.pdf) ISO/IEC 25010 supplies a quality model for specifying product qualities. [[3]](https://www.iso.org/standard/78176.html) Goal-oriented requirements engineering connects goals, requirements, and rationale. [[4]](https://webperso.info.ucl.ac.be/~avl/files/RE01.pdf)

Use [`templates/PROJECT_BRIEF.md`](templates/PROJECT_BRIEF.md).

### 2. Representative journeys

Write enough normal, boundary, failure, or recovery scenarios to clarify the affected requirements. NASA's guidance uses operational concepts and scenarios to describe expected use and stakeholder needs. [[2]](https://www.nasa.gov/wp-content/uploads/2018/09/nasa_systems_engineering_handbook_0.pdf) Scenario count and syntax belong to the project. Add a separate catalogue only when the Project Brief would become difficult to use.

Research on interactive code generation found value in concrete tests and targeted clarification within the studied tasks and participants. [[7]](https://arxiv.org/abs/2404.10100) ClarifyGPT reported improved benchmark results from identifying ambiguity and asking focused questions. [[8]](https://arxiv.org/abs/2310.10996) These studies support clarification and do not establish one universal implementation sequence.

Use [`templates/JOURNEYS.md`](templates/JOURNEYS.md) when a separate catalogue helps.

### 3. Verification and validation record

For every material claim, record:

- the requirement or authority behind it;
- the verification method;
- the procedure or command;
- the expected result;
- the observed result and evidence;
- remaining limits or unresolved risks.

Verification checks specified requirements. Validation checks intended use and stakeholder expectations. Testing, inspection, analysis, and demonstration can support either purpose. Choose the purpose and method that can answer the claim. A passing test proves only what its oracle, inputs, environment, and scope support.

A controlled experiment found traceability improved maintenance-task speed and correctness for its participants and projects. [[5]](https://www.patrickmaeder.de/pdf/ICSM2012_maeder_egyed_AssessingEffectOfRequirementsTraceability.pdf) An industrial multi-case study examined the use of tests as requirements and the communication problems around that practice. [[6]](https://doi.org/10.1016/j.infsof.2016.03.008)

Use [`templates/VERIFICATION.md`](templates/VERIFICATION.md).

## Repository instructions for agents

This playbook packages authoritative paths, commands, constraints, and authorization boundaries in a short project-specific `AGENTS.md`. Linking to detailed material keeps the entry file usable.

One study found generated context files could reduce success and increase inference cost in several evaluated settings. [[9]](https://arxiv.org/abs/2602.11988) Another study associated `AGENTS.md` files with lower median runtime and output-token use while leaving comprehensive semantic-correctness evaluation open. [[10]](https://arxiv.org/abs/2601.20404) Neither study validates this template, its fields, or an ideal length. Those remain packaging choices.

Use [`templates/AGENTS.md`](templates/AGENTS.md).

## Tests and other evidence

Keep the project's existing test strategy. Add or change tests when they are the appropriate verification method for the affected requirement. Review whether the selected evidence can detect the failures that matter.

TestSuiteBench reports that coding agents struggle to generate strong repository-level suites from specifications. [[11]](https://arxiv.org/abs/2610.13065) TENET reports benefits from representative developer-written tests, test-guided retrieval, and iterative failure analysis in its evaluated repository tasks. [[12]](https://arxiv.org/abs/2509.24148)

These findings support careful test selection and review. They do not establish one universal testing sequence, layer split, coverage target, or tool.

## What stays project-specific

The playbook leaves these decisions with the responsible project and its authorities:

- development lifecycle and implementation sequence;
- programming languages, runtimes, frameworks, and package managers;
- test types, tools, coverage goals, and retry policy;
- security, privacy, legal, accessibility, and regulatory controls;
- dependency selection, updates, vulnerability handling, and provenance;
- review independence and release approval;
- deployment, rollback, recovery, and observability;
- evidence retention and candidate-identification requirements.

Use applicable standards and domain guidance when those decisions matter. Record local choices as local choices.

## Research boundary

The sources support the information categories, clarification practices, traceability, and evidence limits described above. They do not establish these Markdown filenames, table layouts, or number of documents as optimal. Those are small packaging choices intended to make adoption easy.

[`research/practice-map.md`](research/practice-map.md) records what each source supports and where its evidence stops.

## Repository map

- [`ADOPT.md`](ADOPT.md): agent-facing adoption instructions.
- [`AGENTS.md`](AGENTS.md): instructions for maintaining this repository.
- [`templates/PROJECT_BRIEF.md`](templates/PROJECT_BRIEF.md): requirements overview.
- [`templates/JOURNEYS.md`](templates/JOURNEYS.md): optional scenario catalogue.
- [`templates/VERIFICATION.md`](templates/VERIFICATION.md): verification and validation record.
- [`templates/AGENTS.md`](templates/AGENTS.md): project instruction template.
- [`examples/minimal-adoption.md`](examples/minimal-adoption.md): worked example.
- [`research/practice-map.md`](research/practice-map.md): evidence boundaries.
- [`research/sources.json`](research/sources.json): citation ledger.
- [`tools/verify_playbook.py`](tools/verify_playbook.py): citation and link checks.

## Verify this repository

```bash
python3 tools/verify_playbook.py
```

The verifier checks the publication set, citation ledger, clickable citations, and local links. It does not judge whether a source truly supports a claim. That requires editorial review.

## Sources

- [[1]](https://www.iso.org/standard/72089.html) ISO/IEC/IEEE 29148:2018 Requirements Engineering
- [[2]](https://www.nasa.gov/wp-content/uploads/2018/09/nasa_systems_engineering_handbook_0.pdf) NASA Systems Engineering Handbook, Revision 2
- [[3]](https://www.iso.org/standard/78176.html) ISO/IEC 25010:2023 Product Quality Model
- [[4]](https://webperso.info.ucl.ac.be/~avl/files/RE01.pdf) van Lamsweerde, *Goal-Oriented Requirements Engineering: A Guided Tour*
- [[5]](https://www.patrickmaeder.de/pdf/ICSM2012_maeder_egyed_AssessingEffectOfRequirementsTraceability.pdf) Mäder and Egyed, *Assessing the Effect of Requirements Traceability for Software Maintenance*
- [[6]](https://doi.org/10.1016/j.infsof.2016.03.008) Bjarnason et al., *A Multi-Case Study of Agile Requirements Engineering and the Use of Test Cases as Requirements*
- [[7]](https://arxiv.org/abs/2404.10100) *LLM-Based Test-Driven Interactive Code Generation: User Study and Empirical Evaluation*
- [[8]](https://arxiv.org/abs/2310.10996) *ClarifyGPT: Empowering LLM-based Code Generation with Intention Clarification*
- [[9]](https://arxiv.org/abs/2602.11988) *Evaluating AGENTS.md: Are Repository-Level Context Files Helpful for Coding Agents?*
- [[10]](https://arxiv.org/abs/2601.20404) *On the Impact of AGENTS.md Files on the Efficiency of AI Coding Agents*
- [[11]](https://arxiv.org/abs/2610.13065) *TestSuiteBench: Coding Agents Struggle to Generate Strong Test Suites from Specifications*
- [[12]](https://arxiv.org/abs/2509.24148) *TENET: One Step Toward Test-Driven Development for Repository-Level Code Generation*

## Status

The repository is ready to adopt. Its packaging is intentionally small. Its claims remain bounded by the cited authorities and studies.
