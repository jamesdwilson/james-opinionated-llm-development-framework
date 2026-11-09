# Adoption instructions

Use this playbook to add a small, research-led context layer to an existing repository.

## Inputs

You need:

- the target repository;
- the requested product or code change;
- authority to inspect files and run existing checks;
- the target repository's authorization boundaries and responsible owners.

## 1. Inspect the repository

Read the material that already governs the work:

- repository instructions;
- product and requirements documentation;
- build, test, and release commands;
- schemas, interfaces, and relevant source code;
- security, privacy, legal, accessibility, or operational policies;
- current working-tree state and local changes.

Apply changes only to the target repository. This playbook's root `AGENTS.md` and verifier govern maintenance of the playbook itself.

This playbook does not select or replace the target repository's infrastructure, lifecycle, or approval process.

## 2. Establish the minimum context

Reuse existing documents where they contain the required information. Create or update only what the work needs:

1. **`AGENTS.md`** with authoritative paths, commands, boundaries, and approvals.
2. **Project Brief** with stakeholders, scope, requirements, constraints, decisions, and acceptance conditions.
3. **Verification and validation record** linking material claims to purposes, methods, procedures, expected results, observed results, and evidence.
4. **Journey catalogue**, only when representative scenarios need more space than the Project Brief provides.

Use the files in `templates/` as small starting points. Combine, rename, or omit them when the repository already has an equivalent source of truth.

## 3. Identify ambiguity

Identify consequential questions that could produce materially different outcomes. Seek targeted clarification from an authoritative source or assign them to the responsible person. Follow the target repository's process for unresolved assumptions.

Record assumptions that remain necessary. Do not present them as established facts.

## 4. Work through the existing process

Follow the target repository's documented development, review, and release authorities. This playbook does not choose their tools or sequence.

For each affected requirement:

1. identify the claim that needs evaluation;
2. decide whether the claim needs verification against a requirement or validation against intended use and stakeholder expectations;
3. choose a suitable method such as testing, inspection, analysis, or demonstration;
4. run the procedure or command;
5. record the observed result and evidence;
6. state what the evidence does not establish.

Unresolved contradictory evidence means the claim remains unresolved.

## 5. Report the result

Leave a concise record containing:

- outcome and affected requirements;
- changed files;
- procedures or commands run;
- observed results and evidence locations;
- unresolved questions, evidence limits, and risks;
- required owner or next action, when work remains.

## Ready-to-use request

```text
Apply the research-led playbook to this repository.
Inspect the target repository and follow its documented authorities and release process.
Create or update only the Project Brief, representative journeys, verification and validation record,
and concise AGENTS.md that the work needs.
Identify consequential ambiguity and seek targeted clarification or record the responsible assumption.
Connect material requirements to suitable verification or validation evidence.
Run the relevant existing checks and report results, limits, and unresolved risks.
```
