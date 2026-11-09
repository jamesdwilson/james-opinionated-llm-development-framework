# Adoption contract

This file is written for the coding agent applying the playbook to another repository.

## Input

You need:

- the target repository;
- the requested profile: Lean, Standard, or High Assurance, with Standard as the default;
- the product or change under consideration;
- authority for file edits and test execution;
- separate approval for new dependencies, external services, deployment, credentials, or public actions.

## Phase 1: inspect

Read the target repository's:

- top-level instructions;
- package or build files;
- test commands;
- CI configuration;
- product documentation;
- main entry points;
- recent relevant changes;
- current working-tree state.

Identify:

- existing sources of truth;
- critical user journeys;
- current test layers;
- runtime and package manager;
- browser-test setup;
- monitoring and recovery path;
- release process;
- security and permission boundaries;
- generated or duplicated contracts;
- local changes that need preservation.

## Phase 2: choose scope

Use the requested profile. Use Standard when the request leaves the profile open. Recommend a smaller or larger profile when the project evidence supports it.

State:

- chosen profile;
- main risk;
- existing pieces to keep;
- missing pieces to add;
- dependencies under consideration;
- work that requires separate approval.

## Phase 3: install the method

Create or update the artefacts required by the selected profile:

1. repository `AGENTS.md`;
2. North Star;
3. journey catalogue;
4. tests for the representative slice;
5. short evidence handoff;
6. acceptance contract for Standard and High Assurance;
7. adversarial review brief for Standard and High Assurance;
8. candidate fingerprint, evidence manifest, and closure rules for High Assurance.

Use the files in `templates/` as starting points. Adapt paths, commands, and wording to the target repository.

## Phase 4: prove one representative slice

Use the current authorised task as the representative slice. When adoption is the only requested change, choose an existing behaviour and improve its instructions, examples, tests, or evidence while preserving product behaviour.

1. Write or identify the rule and examples.
2. Add a failing deterministic check for an authorised behaviour change. Use a focused characterisation or structural verification for behaviour-preserving adoption.
3. Implement the authorised product change, or repair the acceptance gap found in an adoption-only task.
4. Run the narrow check.
5. Run affected integration checks.
6. Run the browser journey when the product has a UI.
7. Exercise one relevant failure and recovery path for Standard and High Assurance.
8. Run the native dependency audit.
9. Record commands and exact results.
10. Run fresh independent review for Standard and High Assurance.

## Phase 5: close honestly

Acceptance requires:

- the selected profile's artefacts;
- all required deterministic checks passing;
- browser evidence required by the selected profile: one representative UI journey for Lean, critical UI journeys for Standard and High Assurance;
- bounded model review only where specified;
- evidence from the exact candidate;
- resolved or explicitly accepted risks;
- fresh review where the profile requires it.

A missing or malformed required record blocks closure.

## Output

Leave a handoff with this shape:

```markdown
## Adoption result

**Profile:**
**Outcome:**
**Representative journey:**

### Changed files
- path: purpose

### Commands and results
- `command` -> exact result

### Evidence
- path or artefact: what it proves

### Remaining risks
- risk: owner and next check

### Next action
- one concrete action
```

## Ready-to-use request

```text
Apply the Standard profile from this playbook to the current repository.
Inspect the repository first and preserve its healthy stack.
Adapt the template paths, commands, and wording to this repository.
Install no dependency without naming the gap it closes and receiving approval.
Prove one representative slice end to end.
Run the resulting checks and leave the required handoff.
```
