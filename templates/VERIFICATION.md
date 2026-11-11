# Verification, validation, and evidence record

Use the project-native identity for the change, artefact, or release being evaluated.

Verification checks specified requirements. Validation checks intended use and stakeholder expectations. Testing, inspection, analysis, and demonstration can support either purpose.

## Subject

- **Candidate or artefact:** `<commit, version, release artefact, or other project-native identity>`
- **Affected requirements:** `<IDs>`
- **BDD journeys:** `<IDs>`
- **Applicable authorities:** `<requirements, standards, policies, contracts, schemas, or owners>`

## Stack map

| Role | Tool or practice used | Version or identity | Substitution or N/A reason |
|---|---|---|---|
| runtime and fast tests | `<value>` | `<value>` | `<value>` |
| browser journeys | `<value>` | `<value>` | `<value>` |
| bounded UX review | `<value>` | `<value>` | `<value>` |
| error capture and recovery | `<value>` | `<value>` | `<value>` |
| supply-chain checks | `<value>` | `<value>` | `<value>` |

## Evidence

| ID | Requirement or claim | Purpose | Owner | Procedure or command | Expected result | Observed result | Evidence |
|---|---|---|---|---|---|---|---|
| V-001 | `<claim>` | `<verification, validation, or advisory observation>` | `<test layer, reviewer, or authority>` | `<procedure>` | `<condition>` | `<result>` | `<path, report, observation, or record>` |

Each final-result artefact identifies the evaluated revision and relevant environment directly or links to a run record that does. Further modifications invalidate affected final evidence.

## TDD record

- **RED revision:** `<preimplementation identity>`
- **RED:** `<check and meaningful failure, or characterisation exception>`
- **GREEN revision:** `<final revision identity>`
- **GREEN:** `<check and result>`
- **REFACTOR:** `<cleanup and recheck, or none>`

## Playwright

- journeys: `<IDs or N/A>`
- command: `<command>`
- result: `<result and report>`

## Midscene

- status: validated release evidence | advisory | N/A
- tool, model, prompt, and fixture identity: `<values>`
- bounded questions: `<questions>`
- observations: `<visible facts>`
- validation record: `<path or N/A>`
- human-labelled sample, agreement criteria, and observed result: `<values or N/A>`
- responsible approver: `<value or N/A>`
- responsible human disposition: `<accepted, rejected, unresolved, or N/A>`

Select `validated release evidence` only when the linked validation record covers the exact configuration and its criteria passed. Otherwise use `advisory`.

## Bugsink recovery exercise

- isolation: `<project or instance>`
- synthetic condition or event: `<value>`
- expected destination: `<value>`
- sensitive-field check: `<result>`
- user-visible behaviour and retained state: `<result>`
- recovery and cleanup: `<result>`

## Supply chain

- resolved graph or lockfile: `<identity>`
- audit command and result: `<value>`
- audit-skipped scoped registries: `<values or none>`
- release-age policy, new-resolution applicability, exemptions, and result: `<value or N/A>`
- accepted exceptions and owner: `<value or none>`

## Evidence limits

- `<excluded condition, unresolved contradiction, uncertainty, or method limit>`

## Result

- **Supported claims:** `<IDs or none>`
- **Unresolved claims:** `<IDs or none>`
- **Review status:** `<project-native status>`
- **Responsible owner and next action:** `<value or none>`
