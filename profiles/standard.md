# Standard profile

## Best fit

- maintained product;
- production releases;
- customer-visible behaviour;
- meaningful persistence or permissions;
- several contributors or coding agents.

## Required artefacts

Everything in Lean, plus:

- acceptance matrix;
- reviewed journey catalogue;
- failure and recovery cases;
- bounded model-review rubric where deterministic checks cannot answer the question;
- evidence record tied to the current candidate;
- adversarial review brief.

## Required checks

- RED test before a behaviour change, or focused characterisation for behaviour-preserving adoption;
- deterministic unit, integration, and contract checks for affected behaviour;
- deterministic browser journeys for critical user flows;
- relevant failure, recovery, and cleanup checks;
- dependency graph review and native audit;
- bounded model review for specified UX questions;
- fresh independent review after ordinary checks pass.

## Evidence

Record:

- a commit after verifying a clean working tree, or a fingerprint of the fully materialised relevant tree covering additions, modifications, deletions, file types, modes, and symlink targets;
- exact command or verification procedure;
- start and end time;
- observed result, including exit code and test counts where applicable;
- report path;
- changed files;
- material runtime and browser versions.

Keep generated reports and evidence outputs outside the candidate input set.

## Closure

A Standard change closes when every required check belongs to the same candidate, evidence is complete, deterministic checks pass, model review stays within its brief, and fresh review finds no unresolved release blocker.
