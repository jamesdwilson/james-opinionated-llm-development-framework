# Project Brief template

This is a concise requirements overview. Link to detailed journeys, schemas, tests, and evidence instead of duplicating them.

## Purpose and outcomes

- **Problem or opportunity:** `<what needs to change>`
- **Desired outcome:** `<observable result for stakeholders>`
- **Success evidence:** `<measure or inspectable condition>`

## Stakeholders and operational context

- **Intended users:** `<users and their context>`
- **Other affected stakeholders:** `<operators, maintainers, customers, regulators, or others>`
- **Operational context:** `<workflow, environment, systems, and interfaces>`

## Scope

### Included

- `<capability or boundary>`

### Excluded

- `<explicit exclusion and reason>`

## Requirements

Give each material requirement a stable ID. State observable behaviour, measurable quality, or a genuine constraint.

| ID | Type | Requirement | Rationale or source | Acceptance condition | Verification link |
|---|---|---|---|---|---|
| R-001 | behaviour | `<observable capability or response>` | `<stakeholder, rule, or source>` | `<pass or fail condition>` | `<test, inspection, analysis, demonstration, or validation>` |
| Q-001 | quality | `<quality attribute with condition and threshold>` | `<risk or stakeholder need>` | `<measurable condition>` | `<verification link>` |
| C-001 | constraint | `<mandatory interface, policy, technology, or limit>` | `<authority and reason>` | `<compliance condition>` | `<verification link>` |

## Representative scenarios

Link to the journey catalogue and identify at least one normal, boundary, and failure scenario where each applies.

- **Normal:** `<journey ID and link>`
- **Boundary:** `<journey ID and link>`
- **Failure or recovery:** `<journey ID and link>`

## Structural constraints and invariants

Record only consequential implementation boundaries. Link to authoritative code or schema definitions.

- `<interface, data owner, invariant, prohibited dependency, or compatibility rule>`

## Assumptions, risks, and open decisions

| ID | Class | Statement | Owner | Next action or resolution date |
|---|---|---|---|---|
| A-001 | assumption | `<environmental fact believed to hold>` | `<owner>` | `<validation action>` |
| RISK-001 | risk | `<condition that could defeat an outcome>` | `<owner>` | `<mitigation or learning action>` |
| D-001 | decision | `<unresolved consequential question>` | `<owner>` | `<decision action and date>` |

## Traceability check

- Every requirement names its rationale or source.
- Every requirement names an acceptance condition.
- Every acceptance condition links to verification evidence.
- Every unresolved decision has an owner and next action.
- Detailed behaviour remains in the journey catalogue.
- Detailed execution evidence remains in the evidence record.
