# Research-to-practice map

This file states what supports each retained practice and where that support ends.

## Evidence labels

- **Standard or handbook:** consensus processes, information categories, or established engineering guidance within a defined scope.
- **Empirical study:** an observed or experimental result limited to its participants, tasks, systems, measures, and design.
- **Packaging choice:** a small repository convention chosen for ease of use. It carries no claim of optimality.

## Project Brief

**Practice:** Record purpose, stakeholders, context, scope, requirements, quality needs, constraints, rationale, assumptions, risks, decisions, acceptance conditions, and verification links.

**Support:** ISO/IEC/IEEE 29148 covers requirements-engineering processes and information items. [[1]](https://www.iso.org/standard/72089.html) NASA's Systems Engineering Handbook covers stakeholder expectations, operational concepts, requirements, verification, and validation. [[2]](https://www.nasa.gov/wp-content/uploads/2018/09/nasa_systems_engineering_handbook_0.pdf) ISO/IEC 25010 supplies a product-quality model. [[3]](https://www.iso.org/standard/78176.html) Goal-oriented requirements engineering connects goals, requirements, and rationale. [[4]](https://webperso.info.ucl.ac.be/~avl/files/RE01.pdf)

**Boundary:** These sources support the information and relationships. They do not establish this filename, Markdown format, table layout, or document count as optimal.

## Scenarios and clarification

**Practice:** Use representative scenarios to clarify expected use. Identify consequential ambiguity and seek targeted clarification where needed.

**Support:** NASA uses operational concepts and scenarios to describe expected use and stakeholder needs. [[2]](https://www.nasa.gov/wp-content/uploads/2018/09/nasa_systems_engineering_handbook_0.pdf) TiCoder found value in test-based interaction for helping participants evaluate generated code in its study. [[7]](https://arxiv.org/abs/2404.10100) ClarifyGPT reported improved benchmark outcomes from identifying ambiguity and asking targeted questions. [[8]](https://arxiv.org/abs/2310.10996)

**Boundary:** The studies used specific programming tasks, benchmarks, systems, and participant groups. They do not establish a universal scenario syntax, count, or implementation sequence.

## Traceability and verification

**Practice:** Connect material requirements to acceptance conditions, verification against requirements, validation against intended use, observed results, evidence, and known limits.

**Support:** A controlled experiment found requirements-to-code traceability improved maintenance-task speed and correctness for its participants and projects. [[5]](https://www.patrickmaeder.de/pdf/ICSM2012_maeder_egyed_AssessingEffectOfRequirementsTraceability.pdf) An industrial multi-case study examined the use of tests as requirements and associated communication challenges. [[6]](https://doi.org/10.1016/j.infsof.2016.03.008) NASA distinguishes verification methods and validation against stakeholder expectations. [[2]](https://www.nasa.gov/wp-content/uploads/2018/09/nasa_systems_engineering_handbook_0.pdf)

**Boundary:** Trace links can be incomplete, stale, or semantically wrong. A recorded link is evidence of bookkeeping until the underlying claim and method are reviewed.

## Repository instructions

**Packaging choice:** Use a project-specific `AGENTS.md` to collect authoritative paths, commands, constraints, and authorization boundaries when the target repository benefits from one.

**Support:** One study found generated context files reduced success and increased inference cost in several evaluated settings. [[9]](https://arxiv.org/abs/2602.11988) Another associated `AGENTS.md` files with lower median runtime and output-token use while leaving comprehensive semantic correctness open. [[10]](https://arxiv.org/abs/2601.20404)

**Boundary:** These findings do not validate this template, its fields, an ideal file length, a section order, or one instruction set for every repository.

## Tests as evidence

**Practice:** Use tests when they can answer the affected claim, and review whether the selected suite can detect relevant failures.

**Support:** TestSuiteBench reports difficulty generating strong repository-level test suites from specifications. [[11]](https://arxiv.org/abs/2610.13065) TENET reports benefits from representative developer-written tests, test-guided retrieval, and iterative failure analysis in its evaluated tasks. [[12]](https://arxiv.org/abs/2509.24148) The industrial requirements study documents both the use and communication limits of tests as requirements. [[6]](https://doi.org/10.1016/j.infsof.2016.03.008)

**Boundary:** These studies do not establish one universal testing sequence, layer split, coverage target, tool, or retry policy.

## Packaging

The repository uses four small templates because they are easy to copy and understand:

- `AGENTS.md`;
- Project Brief;
- optional journey catalogue;
- verification and validation record.

This packaging is a convenience. Projects may combine, rename, or omit files while preserving the supported information and traceability.
