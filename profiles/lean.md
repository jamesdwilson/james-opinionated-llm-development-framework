# Lean profile

## Best fit

- prototype or internal tool;
- small team;
- reversible changes;
- low operational cost of failure;
- short release path.

## Required artefacts

- concise repository `AGENTS.md`;
- North Star;
- representative journey catalogue;
- native test commands;
- short evidence handoff.

## Required checks

- unit tests for changed rules;
- integration checks for changed boundaries;
- one deterministic browser journey for a user-facing product;
- lint, type, or build checks already used by the repository;
- native dependency audit;
- manual review of the changed diff.

## Working rule

Use the repository's existing tools. Add a tool only when the current stack leaves a named acceptance gap.

## Closure

A Lean change closes when required checks pass on the current candidate, the handoff records exact commands and results, and remaining risks have an owner.
