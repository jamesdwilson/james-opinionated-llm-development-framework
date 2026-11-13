# Language and native feedback

This bounded synthesis was checked on 13 November 2026. Study findings, official
language definitions and our operational choices have different evidentiary roles.
The research handbacks supplied search inputs. Claims retained here were checked
against primary text within the scopes recorded in the source ledger.

## Terms used for this decision

For operational review, record when type relationships are checked, which written
annotations the model sees, and which diagnostics a compiler or analysis tool
returns. Treat “strong typing” as a question about specific invalid operations,
conversions and escape hatches. Specify those rules before comparing outcomes.
Annotation presence alone leaves checking configuration and actual feedback unknown.
Haskell's compile-time checking and Erlang's dynamic typing with optional
specifications illustrate why these distinctions matter.
[[34]](https://www.haskell.org/) [[35]](https://www.erlang.org/doc/system/typespec.html)

Treat adoption/popularity as an exposure proxy. Actual model training data,
repository task mix, available tools and documentation quality need separate
assessment. MultiPL-E uses public frequency categories and finds both a general
association and niche-language exceptions. Its translated function completions,
older Codex/CodeGen/InCoder models and prompt-sensitive results limit transfer to
repository agents. It supplies no project documentation-quality measure.
[[32]](https://arxiv.org/html/2208.08227)

## Empirical findings and disconfirmation

- **Diagnostic feedback.** Type-Error Ablation and AI Coding Agents reports that
  richer type diagnostics generally helped repair programs with one deliberate
  Shplait type error. The primary setup uses qwen2.5-coder:14b with aider, with
  additional Claude Haiku 4.5 rounds. The test-only condition changes both typing
  and feedback format. Small programs, one language and test-defined success
  bound the result. Long-horizon repository success and a causal language ranking
  remain unestablished. [[29]](https://arxiv.org/html/2606.01522v2)

- **Generation constraints.** Type-Constrained Code Generation reports improved
  compilation and functional benchmark outcomes from specialised decoding on a
  TypeScript subset. The inspected abstract/introduction support a result about
  that generation technique. Ordinary compiler invocation and selection of a
  static language alone have different interventions.
  [[31]](https://arxiv.org/pdf/2504.09246v2)

- **Annotation counterevidence.** Enriching Source Code with Contextual Data
  reports small improvements after removing TypeScript annotations for older
  token/line-completion models. The inspected abstract/introduction concern
  textual completion metrics. Current repository-agent behavior and the value of
  retaining useful project types remain unmeasured in that comparison.
  [[30]](https://arxiv.org/pdf/2304.12269)

- **Within-study qualifications.** MultiPL-E reports a benefit from precise
  TypeScript signatures over `Any`, alongside null Python-annotation and
  TypeScript-checking comparisons. These finite comparisons support task-dependent
  interpretation of type information. [[32]](https://arxiv.org/html/2208.08227)

- **Underrepresented-language counterevidence.** Longtail-SWE includes Haskell
  and Erlang and reports strong averaged outcomes on their subsets. Different task
  populations, repository filters, solver-guided construction and selection,
  possible contamination and configuration differences prevent causal language
  ranking. Its threats section expressly bounds language differences to sampled
  tasks and evaluated configurations. No numerical language scores are adopted
  here. [[33]](https://arxiv.org/html/2611.10304v2)

## Official language definitions

Haskell checks expression types at compile time. Erlang is dynamically typed.
Its specifications can document interfaces and inform tools such as Dialyzer.
For this policy, record that analysis separately from static-language checking.
[[34]](https://www.haskell.org/) [[35]](https://www.erlang.org/doc/system/typespec.html)

BEAM names the Erlang virtual machine. Gleam has a static type system and can
compile for that runtime, providing a useful contrast within the BEAM ecosystem.
The FAQ's coding-agent answer is an unmeasured maintainer statement. No measured
Gleam agent result was established by this review.
[[36]](https://gleam.run/frequently-asked-questions/)

## Our operational choice

Retain and use applicable project-native compiler, typechecker and analysis
feedback together with behavioral checks. The project owner reviews the mapping
of explicit commands to existing roles. Inspect documentation for the actual
versions, APIs, examples and task being exercised. Assess documentation directly
and leave its quality unknown until inspected.

Use the existing [manual plan and reviewed application bridge](../ADOPT.md#2-map-the-stack).
The reviewed literal-gate editor appends missing commands. Manual transfer replaces
selected whole lists, so review and merge required checks before consciously
replacing a role. Keep command ownership and guide preservation under the existing
contracts. Language, type-system and popularity labels alone never qualify support,
readiness or agent success. There is no language ranking, whitelist or migration
rule in this policy.

The candidate adds preservation contracts for synthetic Haskell, Erlang and Gleam
metadata and owner-supplied compiler/analysis and behavioral command lists. Those
command strings are examples awaiting project review. They supply no native-tool
execution evidence. The existing bridge needs no new selection engine, schema or
dependency for this policy.

No universal benefit or optimum is established. Applicability to the current
pinned-agent configuration remains unknown, including for Haskell and Erlang.
