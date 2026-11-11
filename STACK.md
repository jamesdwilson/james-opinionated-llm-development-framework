# Cohesive stack

This file defines the default roles and how they connect. Keep sound equivalents already present in the target repository. Add a default only when its role is missing and installation is authorised.

## Stack map

| Stage | Purpose | Default | Evidence class | Replacement rule |
|---|---|---|---|---|
| Project Brief | requirements, context, constraints, acceptance | Markdown template | standards and research | keep an equivalent requirements source |
| BDD discovery | rules, examples, questions, scenarios | Example Mapping and Given, When, Then | practitioner method with adjacent empirical support | keep an equivalent scenario practice |
| TDD implementation | short implementation feedback loop | RED, GREEN, REFACTOR | James's stack choice with related empirical support | keep an established test-guided loop if it provides the same discipline |
| Fast deterministic checks | rules, boundaries, contracts | Bun test for new JS/TS work | documented capability | use the repository's native runner |
| Browser journeys | rendered, stateful behaviour | Playwright | maintainer guidance and documented capability | keep an established browser runner with equivalent coverage |
| Bounded UX review | visible clarity and friction | Midscene with Playwright | documented capability; advisory until locally validated | use human review or a validated equivalent |
| Error and recovery exercise | telemetry and recovery evidence | isolated Bugsink project or disposable instance | documented capability plus project requirements | keep an isolated equivalent tracker |
| Supply chain | resolved graph, advisories, publication delay | Bun audit and minimumReleaseAge | documented capability plus NIST guidance | use the package manager and security policy already authorised |
| Candidate evidence | connect results to the evaluated change | Git or project-native release identity | SLSA-informed provenance | use the identity trusted by the project |
| Final challenge | catch weak evidence and unsupported conclusions | project reviewer, fresh agent, or human | engineering reports and local process | follow the repository's review authority |

## Joined-up authority

Each stage passes a concrete object to the next:

1. The Project Brief supplies requirement IDs and acceptance conditions.
2. BDD examples expose interpretations, edge cases, and open questions.
3. TDD turns one example or rule into an executable implementation step.
4. Deterministic checks own claims that can be computed or asserted.
5. Playwright owns rendered interaction and browser state.
6. Midscene adds bounded observations about visible clarity.
7. Bugsink exercises operational error capture and a relevant recovery path.
8. Supply-chain checks inspect the dependencies used by the revision.
9. The verification record connects claims, procedures, results, and limits to the project-native revision identity.
10. Review challenges the complete chain.

A later stage cannot excuse a failed claim owned by an earlier stage. A model observation cannot overrule a failed test. A passing test cannot establish a usability conclusion it never measured.

## Default commands for a new Bun project

Adapt paths and scripts to the target repository.

```bash
bun install
bun test
bunx playwright test
bun audit
```

Midscene and Bugsink need project-specific scripts because journeys, providers, credentials, isolation, and data boundaries vary. Put those scripts in the target repository and list them in its `AGENTS.md`.

## Midscene boundary

Declare:

- the exact journey;
- the narrow visual question;
- the tool, model, prompt, and fixture identity;
- the visible observations;
- the deterministic results for the same change;
- whether responsible human judgement has validated this use.

Validated status requires a linked validation record for the exact tool, model, prompt, and fixture configuration. That record states the human-labelled sample, agreement criteria, observed result, and responsible approver. Until those criteria pass, Midscene findings remain advisory and unresolved disagreement goes to the responsible human authority.

## Bugsink boundary

Use synthetic data. Isolate the exercise from production. Record:

- the injected condition or synthetic event;
- the expected capture destination;
- sensitive fields that must stay absent;
- the product's specified user-visible behaviour;
- recovery and cleanup results.

The stack selects Bugsink as the default target. The product requirement selects the failure and expected recovery.

## Supply-chain boundary

The default checks inspect the resolved graph and available advisory data. `minimumReleaseAge` applies during new resolution and does not retroactively evaluate packages already present in `bun.lock`. `bun audit` may skip a scoped registry without an advisory endpoint while retaining a successful exit code. Record age-gate applicability, exemptions, and any skipped registry. These checks do not prove that every dependency is benign. The target project's security authority owns:

- acceptable versions and provenance;
- release-age policy;
- emergency update exceptions;
- advisory disposition;
- rollback and update cadence.

## Substitution test

Keep an existing tool when all three statements are true:

1. it owns the same claim or operational role;
2. its output can enter the same verification record;
3. replacing it would add risk or duplicate infrastructure without closing a demonstrated gap.

Record the substitution in the adoption stack map. This preserves cohesion while respecting a working repository.

Missing authorization, unavailable tooling, or an unexecuted required role is `blocked` or `not run`, not N/A. Use N/A only when the product and authorised scope make the role genuinely inapplicable.

## Evidence binding

Each final-result artefact identifies the evaluated revision directly or links to a run record containing the revision and relevant environment. Record RED against its earlier revision separately. A further modification invalidates affected final evidence and requires those checks to run again.
