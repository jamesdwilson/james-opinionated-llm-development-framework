# James's opinionated LLM development framework

> A practical stack for taking an idea through implementation, browser testing, failure recovery, and release evidence.

Here's how it works. I've made the tough choices and done the research so you don't have to. Start with this stack, keep the tools you already like, and add only what is genuinely useful.

The whole thing runs as one chain:

```text
Project Brief
  -> BDD rules, examples, and questions
  -> RED, GREEN, REFACTOR
  -> unit, integration, and contract checks
  -> Playwright browser journeys
  -> bounded Midscene UX review
  -> Bugsink failure and recovery exercise
  -> Bun audit and release-age controls
  -> candidate-bound evidence
  -> independent challenge and handoff
```

This is meant to work as one system rather than a pile of unrelated tools. The brief defines the job. BDD removes ambiguity. TDD drives the change. Deterministic tests check the facts. Playwright exercises the real interface. Midscene gives the finished interface a visual sanity check. Bugsink captures errors during a separately checked recovery exercise. Supply-chain checks inspect what you are actually installing. Evidence and review tie the results to the exact change under consideration.

## Why use it

- **Less guesswork.** Every part of the stack has a clear job.
- **Less, on purpose.** Fewer overlapping tools, dependencies, abstractions, and instructions give people and LLMs less to configure, patch, and misunderstand.
- **Easy to adopt.** Keep sound tools already in the project and add only the missing pieces.
- **Opinionated on purpose.** Bun, Playwright, Midscene, and Bugsink are the defaults, so the agent does not reopen the same tooling debate on every task.
- **Honest about evidence.** Research informs the method, official documentation establishes tool capabilities, and stack preferences stay labelled as preferences.
- **Easy to inspect.** Important claims point back to a requirement, test, observation, or accountable decision maker.

## Less is more

Use the smallest set of tools, dependencies, abstractions, code paths, and instructions that can prove the job is done. Every extra layer should earn its keep.

That lines up with performance and security, but it is a design direction rather than a magic guarantee. Less unnecessary work can mean less overhead. A smaller dependency set and fewer code paths also leave fewer things to review, update, and defend. Measure the real project instead of assuming that smaller is automatically faster or safer. ISO/IEC 25010 treats performance efficiency, security, and maintainability as explicit product qualities, while NIST's Secure Software Development Framework covers third-party components and secure development practices. [[3]](https://www.iso.org/standard/78176.html) [[23]](https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-218.pdf)

The agent research points in the same general direction without proving that less always wins. One study found that generated repository context could increase inference cost and sometimes reduce task success, while Skeleton Coding found benefits from concise structural specifications in its evaluated settings. [[9]](https://arxiv.org/abs/2602.11988) [[14]](https://arxiv.org/abs/2610.38214)

## Start here

Point your coding agent at the repository and give it this:

```text
Read https://github.com/jamesdwilson/james-opinionated-llm-development-framework

Read this playbook's ADOPT.md and STACK.md.
In the target repository, read its own instructions and inspect its current stack.
Map existing tools to the playbook roles and keep sound equivalents.
Add only the missing roles needed for the authorised work.
Apply the full chain to one representative slice:
Project Brief, BDD examples, TDD implementation, deterministic checks,
Playwright journey, bounded UX review where useful, Bugsink recovery exercise
where operational errors matter, supply-chain checks, and candidate-bound evidence.
Run the target repository's required checks and report results, limits, and risks.
```

[`ADOPT.md`](ADOPT.md) explains how to bring the stack into an existing project. [`STACK.md`](STACK.md) defines each role, default tool, substitution rule, and evidence boundary.

## What gets the final say

Each decision should follow the source that actually owns it:

- stakeholders and product requirements for intended outcomes;
- laws, standards, policies, and contracts for mandatory constraints;
- schemas, interfaces, source code, and existing tests for current technical contracts;
- verification and validation evidence for the claims those methods can actually answer;
- empirical research within its studied population, tasks, measures, and limitations;
- official documentation for a tool's supported capabilities.

Treat the stack as a useful default, not a rule you have to follow. It does not outrank the law, a product decision, or a proven project-specific constraint.

## Suggested stack

| Stack | Why |
| --- | --- |
| [Project Brief](#stack-project-brief) | It tells the LLM what game we are playing before it starts moving pieces. |
| [BDD and Example Mapping](#stack-bdd) | They turn "make it work" into examples people can agree on before anyone writes code. |
| [TDD](#stack-tdd) | It gives the model a real failing target instead of letting it guess what needs fixing. |
| [Deterministic tests](#stack-deterministic-tests) | They are boring in the best way: same code, same answer, no model mood swings. |
| [Bun](#stack-bun) | It covers the runtime, installs, and tests in one tool, with fast package installs and dependency scripts limited to trusted packages. |
| [Playwright](#stack-playwright) | It clicks through the real interface and catches user-visible failures that unit tests often miss. |
| [Midscene](#stack-midscene) | It is cool because it catches the "this technically works, but feels confusing" problems hard tests usually miss. |
| [Bugsink](#stack-bugsink) | It lets you rehearse failure safely and prove the error went where it should. |
| [Supply-chain checks](#stack-supply-chain) | They show what you are really installing and can give brand-new packages time to settle. |
| [Evidence tied to the build](#stack-candidate-evidence) | It answers "which exact build passed?" instead of trusting a loose green screenshot. |
| [Fresh eyes before done](#stack-independent-review) | A separate reviewer checks the work before the builder grades their own homework. |

## How each piece works

Plain English comes first. The research, caveats, and implementation detail stay underneath for the clankers who want to inspect the machinery.

<a id="stack-project-brief"></a>
### 1. Project Brief

A Project Brief gives the LLM a map before asking it to drive. It says who the product is for, what success looks like, what is out of scope, and what evidence counts. That helps a fluent agent avoid building a polished answer to the wrong question.

**Under the hood:** capture purpose, outcomes, stakeholders, context, scope, requirements, quality attributes, constraints, assumptions, risks, decisions, acceptance conditions, and evidence links. ISO/IEC/IEEE 29148 covers requirements-engineering processes and information items. [[1]](https://www.iso.org/standard/72089.html) NASA's Systems Engineering Handbook covers stakeholder expectations, operational concepts, requirements, verification, and validation. [[2]](https://www.nasa.gov/wp-content/uploads/2018/09/nasa_systems_engineering_handbook_0.pdf) ISO/IEC 25010 supplies a product-quality model. [[3]](https://www.iso.org/standard/78176.html) Goal-oriented requirements engineering connects goals, requirements, and rationale. [[4]](https://webperso.info.ucl.ac.be/~avl/files/RE01.pdf)

Use [`templates/PROJECT_BRIEF.md`](templates/PROJECT_BRIEF.md).

<a id="stack-bdd"></a>
### 2. BDD and Example Mapping

BDD turns fuzzy language into examples people can actually discuss. "Make checkout simple" is vague. A few concrete examples of what happens, what can go wrong, and how the user recovers give the LLM something solid to build.

**Under the hood:** turn requirements into rules, examples, and open questions. Use Given, When, Then when it helps, and cover normal, boundary, failure, and recovery behaviour where it matters. Example Mapping is the selected discovery technique. [[13]](https://cucumber.io/docs/bdd/example-mapping/) NASA supports operational scenarios as part of understanding expected use. [[2]](https://www.nasa.gov/wp-content/uploads/2018/09/nasa_systems_engineering_handbook_0.pdf) TiCoder and ClarifyGPT provide empirical support for concrete tests and targeted clarification within their studied tasks. [[7]](https://arxiv.org/abs/2404.10100) [[8]](https://arxiv.org/abs/2310.10996)

Use [`templates/JOURNEYS.md`](templates/JOURNEYS.md).

<a id="stack-tdd"></a>
### 3. TDD: RED, GREEN, REFACTOR

TDD makes the model show the problem before it fixes it. RED proves the check can catch the missing or broken behaviour. GREEN shows that the smallest repair satisfies the relevant checks. REFACTOR cleans things up without losing that evidence.

```text
RED -> GREEN -> REFACTOR
```

**Under the hood:** write or identify a meaningful failing check for the behaviour being changed. Make the smallest coherent change that satisfies it. Clean up only while the relevant checks stay green. If behaviour should not change, start from a verified green characterisation instead of manufacturing a failure.

Across 20 diverse web applications, TDDev reports accuracy gains of 15.5 to 23.7 percentage points with sufficiently capable backbones; a stronger tester restored positive gains for a lower-capability backbone. [[15]](https://arxiv.org/abs/2605.17242) TENET reports benefits from representative developer-written tests, retrieval guided by tests, and iterative failure analysis. [[12]](https://arxiv.org/abs/2509.24148) TestSuiteBench shows that coding agents still struggle to create strong repository-level test suites from specifications. [[11]](https://arxiv.org/abs/2610.13065)

Full RED, GREEN, REFACTOR is the chosen operating discipline here. The research supports test-guided repair in the settings it studied. It does not prove that the complete sequence is universally best.

<a id="stack-deterministic-tests"></a>
### 4. Deterministic tests

Deterministic tests are boring in the best way. They do not get tired, creative, or persuaded by a confident explanation. The same code and inputs should produce the same answer every time.

**Under the hood:** use the simplest test that can answer the question reliably:

- unit checks for pure rules and transformations;
- integration checks for persistence, services, queues, and adapters;
- contract checks for schemas and interfaces;
- browser checks for rendered, stateful user journeys.

Program structure can also reduce ambiguity for coding agents. Skeleton Coding reports benefits from structural specifications in its evaluated settings. [[14]](https://arxiv.org/abs/2610.38214)

The exact split is a stack convention. Keep an existing test layer when it already answers the same question cleanly.

<a id="stack-bun"></a>
### 5. Bun

Bun earns its place by replacing a small pile of JavaScript tooling with one fast tool. It can run the code, install packages, and run tests, which means less setup and fewer version seams for people and LLMs to keep straight.

**Under the hood:** Bun's test runner is designed to feel familiar to Jest users. [[18]](https://bun.com/docs/test) Bun's own benchmark reports `bun install` as up to 25 times faster than npm. Bun also limits dependency lifecycle scripts to trusted packages, including a built-in allowlist. Those are useful defaults, not a promise that every Bun application will be faster or safer than every Node application. [[27]](https://bun.com/docs/pm/cli/install) [[28]](https://bun.com/docs/pm/lifecycle)

If you're a big fan of Node or do not want to use Bun, don't worry about it. Keep Node when it is working well. Bun's package manager can also be used in an existing Node project, so trying it does not have to be an all-or-nothing migration. [[27]](https://bun.com/docs/pm/cli/install)

<a id="stack-playwright"></a>
### 6. Playwright

Playwright closes the awkward gap between "the function passed" and "the app works." It opens the real page, clicks the real controls, reloads, and checks what is actually visible to expose user-facing failures lower-level tests may miss.

**Under the hood:** Playwright owns critical rendered journeys including visible state, interaction, permissions, reloads, client-side recovery, and user-observable persistence. It recommends isolated tests, user-facing assertions, resilient locators, and web-first waiting. [[16]](https://playwright.dev/docs/best-practices) Its planner, generator, and healer agents can assist test creation while executable assertions remain the behavioural evidence. [[17]](https://playwright.dev/docs/test-agents)

<a id="stack-midscene"></a>
### 7. Midscene

Midscene is cool because it can look at the rendered interface and call out the annoyingly human stuff hard assertions miss. It notices when a flow technically works but still feels confusing. It adds AI-assisted interaction and visual assertions through Playwright. [[19]](https://midscenejs.com/integrate-with-playwright.html)

Use it for narrow questions such as:

- Is the required choice understandable?
- Is the next action visually apparent?
- Does the completed state explain what happened?
- Is the recovery path visible after the exercised failure?

**Under the hood:** Midscene is advisory by default. It cannot overrule a failed deterministic check. Count its output as release evidence only after the project has validated the model, prompt, fixtures, and agreement with responsible human judgement.

<a id="stack-bugsink"></a>
### 8. Bugsink

Bugsink lets you rehearse failure before a real user finds it. Trigger a safe synthetic error, prove it reached the error tracker without leaking sensitive data, and separately check that the product recovered the way it promised.

**Under the hood:** use synthetic data and an isolated Bugsink project or disposable instance. Bugsink is a self-hosted Sentry-compatible target. [[20]](https://www.bugsink.com/docs/) The product requirement chooses the failure worth exercising. Check capture in Bugsink, verify recovery through the deterministic or browser layer that owns that behaviour, and confirm cleanup works.

<a id="stack-supply-chain"></a>
### 9. Supply-chain checks

Supply-chain checks answer the question hidden behind "it installed": what did we actually install? They make dependency changes visible, check known advisories, and can keep very new package releases out until they have had time to settle.

**Under the hood:** keep dependency changes boring and reversible. For Bun projects:

- commit the lockfile;
- review dependency-graph changes;
- run `bun audit` against the resolved graph;
- use `minimumReleaseAge` when the project's risk policy calls for a publication delay;
- record exceptions and rollback.

Bun documents its audit command and release-age control. [[21]](https://bun.com/docs/pm/cli/audit) [[22]](https://bun.com/docs/runtime/bunfig) [[27]](https://bun.com/docs/pm/cli/install) NIST's Secure Software Development Framework supplies broader secure-development guidance. [[23]](https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-218.pdf)

The release-age filter applies during new resolution. It does not go back and judge packages already present in `bun.lock`. An audit may also skip a scoped registry that has no advisory endpoint without changing the exit code. Record both conditions. This playbook does not set one universal quarantine period; the responsible security authority owns that choice.

<a id="stack-candidate-evidence"></a>
### 10. Evidence tied to the exact build

Evidence tied to the build gets rid of the vague "it passed on my machine yesterday" claim. Every test result points to the exact commit, build, commands, and environment that produced it.

**Under the hood:** record the project-native candidate identity, exact commands or procedures, observed results, report locations, relevant environment facts, and evidence limits. Use a clean commit, release artefact, or another identity the project already trusts. SLSA provenance provides a model for connecting an artefact to its build context. [[24]](https://slsa.dev/spec/v1.2/provenance) A controlled traceability experiment found maintenance benefits for its participants and projects. [[5]](https://www.patrickmaeder.de/pdf/ICSM2012_maeder_egyed_AssessingEffectOfRequirementsTraceability.pdf) An industrial multi-case study documents both the use and communication limits of tests as requirements. [[6]](https://doi.org/10.1016/j.infsof.2016.03.008)

Use [`templates/VERIFICATION.md`](templates/VERIFICATION.md).

<a id="stack-independent-review"></a>
### 11. Fresh eyes before done

Fresh eyes matter because the builder already knows what they intended. A separate reviewer sees only what the exact candidate and its evidence actually prove, which makes weak tests, stale evidence, missing requirements, and overconfident conclusions easier to spot.

**Under the hood:** record what changed, what ran, what passed, what remains uncertain, and who owns the next decision. OpenAI and Anthropic engineering reports emphasise repository legibility, mechanical checks, durable progress, and useful handoffs in long-running agent work. [[25]](https://openai.com/index/harness-engineering) [[26]](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)

The project can choose the reviewer and handoff format. The important bit is that the final challenge is genuinely independent of the person or agent that made the change.

## Repository instructions

Keep `AGENTS.md` short enough that an agent can actually use it. Connect the stack to the target repository's real paths, commands, boundaries, and evidence. One study found generated context files could reduce success and increase inference cost in several evaluated settings; its aggregate success differences were not statistically significant. [[9]](https://arxiv.org/abs/2602.11988) Another associated existing `AGENTS.md` files with lower median runtime and output-token use while leaving comprehensive semantic-correctness evaluation open. [[10]](https://arxiv.org/abs/2601.20404)

Neither study validates this template or tells us the perfect file length. [`templates/AGENTS.md`](templates/AGENTS.md) is simply the format chosen here.

## Adoption rule

If an existing tool already does the job well, keep it. There is no need to replace something you like just because this README names a different default. Record the equivalence in the stack map, and add the suggested tool only when the role is missing, the task needs it, and installation is authorised.

The goal is a joined-up method, not a rewrite for the sake of one.

## What the research does and does not prove

[`research/practice-map.md`](research/practice-map.md) labels each part as:

- standard or handbook guidance;
- empirical evidence;
- documented capability;
- engineering report;
- James's stack choice.

A capability page can show that a tool supports a function. It cannot prove that the tool is best for everyone. A study supports only the population, tasks, measures, and design it actually examined.

## Repository map

- [`STACK.md`](STACK.md): roles, defaults, substitutions, and evidence boundaries.
- [`ADOPT.md`](ADOPT.md): agent-facing adoption procedure.
- [`AGENTS.md`](AGENTS.md): maintenance instructions for this source repository.
- [`templates/PROJECT_BRIEF.md`](templates/PROJECT_BRIEF.md): requirements overview.
- [`templates/JOURNEYS.md`](templates/JOURNEYS.md): BDD rules and scenarios.
- [`templates/VERIFICATION.md`](templates/VERIFICATION.md): verification, validation, and evidence record.
- [`templates/AGENTS.md`](templates/AGENTS.md): target-repository instruction template.
- [`checklists/release.md`](checklists/release.md): cohesive-stack completion check.
- [`examples/cohesive-adoption.md`](examples/cohesive-adoption.md): worked example.
- [`research/practice-map.md`](research/practice-map.md): evidence map and limits.
- [`research/sources.json`](research/sources.json): citation ledger.
- [`tools/verify_playbook.py`](tools/verify_playbook.py): citation and local-link checks.

## Verify this repository

```bash
python3 tools/verify_playbook.py
```

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
- [[13]](https://cucumber.io/docs/bdd/example-mapping/) Cucumber Example Mapping
- [[14]](https://arxiv.org/abs/2610.38214) *Skeleton Coding: Program Structure as a Specification for Agents*
- [[15]](https://arxiv.org/abs/2605.17242) *From Runnable to Shippable: Multi-Agent Test-Driven Development for Generating Full-Stack Web Applications from Requirements*
- [[16]](https://playwright.dev/docs/best-practices) Playwright Best Practices
- [[17]](https://playwright.dev/docs/test-agents) Playwright Test Agents
- [[18]](https://bun.com/docs/test) Bun Test Runner
- [[19]](https://midscenejs.com/integrate-with-playwright.html) Midscene Playwright Integration
- [[20]](https://www.bugsink.com/docs/) Bugsink Documentation
- [[21]](https://bun.com/docs/pm/cli/audit) Bun Audit
- [[22]](https://bun.com/docs/runtime/bunfig) Bun Configuration
- [[23]](https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-218.pdf) NIST Secure Software Development Framework
- [[24]](https://slsa.dev/spec/v1.2/provenance) SLSA Provenance
- [[25]](https://openai.com/index/harness-engineering) OpenAI Harness Engineering
- [[26]](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) Anthropic Effective Harnesses for Long-Running Agents
- [[27]](https://bun.com/docs/pm/cli/install) Bun Install and Minimum Release Age
- [[28]](https://bun.com/docs/pm/lifecycle) Bun Lifecycle Scripts

## Status

The suggested stack is ready to use. It is deliberately opinionated, but not dogmatic. Tool choices are explicit, substitutions are allowed, and research claims stay within what their sources actually establish.
