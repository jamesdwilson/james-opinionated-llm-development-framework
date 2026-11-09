# Adoption instructions

Apply the cohesive stack to an existing repository without discarding sound equivalents.

These instructions govern the target repository. The playbook source repository's root `AGENTS.md` and verifier are maintenance tools for the playbook itself.

## Inputs

You need:

- the target repository and authorised change;
- its product, technical, security, and release authorities;
- authority to inspect files and run existing checks;
- approval under the target repository's rules before adding dependencies, services, credentials, or release actions.

## 1. Inspect the target

Read:

- repository instructions and product documentation;
- build, test, browser, audit, and release commands;
- schemas, interfaces, and affected source code;
- security, privacy, legal, accessibility, and operational policies;
- monitoring and recovery paths;
- current working-tree state and local changes.

## 2. Map the stack

Create a short adoption map:

| Role | Existing tool or practice | Keep, add, N/A, blocked, or not run | Reason |
|---|---|---|---|
| Project Brief | `<value>` | `<decision>` | `<authority or gap>` |
| BDD discovery | `<value>` | `<decision>` | `<authority or gap>` |
| TDD and fast tests | `<value>` | `<decision>` | `<authority or gap>` |
| Browser journeys | `<value>` | `<decision>` | `<authority or gap>` |
| Bounded UX review | `<value>` | `<decision>` | `<authority or gap>` |
| Error capture and recovery | `<value>` | `<decision>` | `<authority or gap>` |
| Supply-chain checks | `<value>` | `<decision>` | `<authority or gap>` |
| Candidate evidence and review | `<value>` | `<decision>` | `<authority or gap>` |

Use the defaults in `STACK.md` for missing roles. Keep sound equivalents. Mark a role N/A only when the product or authorised change genuinely does not exercise it. Missing authorization, unavailable tooling, or an unexecuted required role is blocked or not run. Preserve every role and its disposition in the authoritative adoption map.

## 3. Establish the context

Reuse existing documents where they contain the required information. Add only missing information:

1. target-repository `AGENTS.md` with real paths, commands, boundaries, approvals, and a link to the authoritative adoption map;
2. Project Brief with requirements, constraints, acceptance conditions, and evidence links;
3. BDD rules, examples, and questions for the representative slice;
4. verification and validation record for the evaluated change.

The templates may be combined, renamed, or embedded in existing project documentation.

## 4. Implement one representative slice

Follow this chain:

1. identify the affected requirement and acceptance condition;
2. map rules, examples, and unresolved questions;
3. resolve consequential ambiguity or record the responsible assumption;
4. establish meaningful RED for changed behaviour, or a green characterisation baseline for behaviour-preserving work;
5. implement the smallest coherent change and reach GREEN;
6. refactor while relevant checks remain green;
7. run affected unit, integration, and contract checks;
8. run the Playwright journey or the target's equivalent browser check;
9. run bounded Midscene review when the slice contains a useful visual question;
10. exercise a relevant Bugsink recovery path when operational errors are in scope;
11. run the target's dependency and supply-chain checks;
12. bind each final report to the evaluated candidate and relevant environment, keeping RED tied to its earlier candidate;
13. complete the target repository's independent review and release process.

A failed deterministic check remains a failure. Midscene findings are advisory until the project validates that evaluation setup.

## 5. Report the result

Leave:

- the adoption stack map;
- affected requirements and scenarios;
- changed files;
- procedures and commands run;
- observed results and evidence locations;
- Midscene validation status and findings where used;
- Midscene validation-record path, agreement criteria, result, and approver when validated status is claimed;
- Bugsink isolation, data, recovery, and cleanup results where used;
- supply-chain results and accepted exceptions;
- evidence limits, unresolved risks, and responsible owners.

## Ready-to-use request

```text
Apply the cohesive stack from this playbook to the target repository.
Read STACK.md, then inspect the target's own instructions and tools.
Map every stack role to an existing equivalent, a justified default, N/A,
blocked, or not run. Give the reason for every disposition.
Keep sound equivalents and add only missing roles within current authority.
Apply Project Brief, BDD, TDD, deterministic checks, Playwright, bounded Midscene,
Bugsink recovery, supply-chain checks, and candidate-bound evidence to one
representative slice. Run the target repository's required checks and report
results, evidence limits, substitutions, and unresolved risks.
```
