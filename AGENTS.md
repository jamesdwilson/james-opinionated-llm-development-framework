# AGENTS.md

## Mission

Help developers adopt this playbook in an existing repository with the smallest useful change set.

## Start here

1. Read `README.md`.
2. Read `ADOPT.md`.
3. Use the requested profile. Use Standard when the request leaves the profile open.
4. Inspect the target repository before proposing files or tools.
5. Reuse healthy commands, conventions, and test infrastructure.

## Playbook check

Run `python3 tools/verify_playbook.py` after changing prose, citations, links, or the source ledger.

## Authority rules

- Every applicable required deterministic check must pass.
- Browser tests own visible mechanics and stateful journeys.
- Model review answers bounded questions about clarity, hierarchy, ambiguity, and friction.
- Security and permission failures stop acceptance.
- `RED` or `UNCLEAR` on a required product journey stops acceptance.
- Expected `RED` on an isolated negative control passes that control.
- Evidence belongs to the exact candidate under review.
- A fresh reviewer challenges implementation and acceptance machinery.

## Adoption rules

- Create only the artefacts the selected profile requires.
- Preserve one source of truth for each contract.
- Name the gap before adding a dependency.
- Add abstraction on its second real use.
- Prefer native semantics, stable names, and short dependency paths.
- Keep agent instructions concise and executable.
- Record exact commands or procedures and results.
- Leave one concrete next action.

## Writing style

Use plain, direct language. Lead with the recommendation. Prefer concrete verbs and specific nouns.

Avoid:

- formulaic contrasts;
- throat-clearing introductions;
- inflated claims;
- fake quotations;
- generic conclusions;
- repeated summaries;
- decorative jargon;
- long chains of parenthetical caveats.

## Repository boundary

This repository contains a method, profiles, templates, checklists, examples, and research links. It contains no active product lab.

When applying the method elsewhere, edit the target repository. Keep this repository as the source playbook unless the task explicitly asks for a playbook change.

## Required handoff

Report:

- selected profile and reason;
- files changed;
- commands or procedures run;
- exact results;
- evidence paths;
- remaining risks;
- next concrete action.
