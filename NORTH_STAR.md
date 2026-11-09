# North Star v1: household task confidence

## Target user

A household member using the product for the first time, with no knowledge of internal task-system terminology.

## Job

Create a household task, decide whether completion needs another person's approval, complete it, and understand who did what without asking how the system works.

## Desired experience

- Choices describe practical outcomes rather than internal categories.
- The next required action is visible and predictable.
- Permission boundaries are explained without blame.
- Reloading never erases accepted work.
- History distinguishes creator, completion requester and approver.
- Errors preserve entered work and show a visible recovery path.

## Anti-goals

- Exposing internal labels such as `Core` or `Required`.
- Allowing the person who requested completion to approve their own request.
- Treating a toast, screenshot or model opinion as proof of persistence.
- Hiding actor identity or inventing provenance.
- Adding AI actions to the product merely to call it AI-first.

## Authority and truth boundaries

Playwright and deterministic tests own application state, contracts, permissions, persistence, provenance, accessibility mechanics and cleanup. Midscene may judge visible clarity, hierarchy, coherence, terminology, progress and recovery only. `RED` fails. `UNCLEAR` cannot pass. `GREEN` is admissible only when deterministic gates pass on the same candidate.

## Success signals

A reasonable first-time user can complete the corrected journey without unexplained terms, ambiguous required choices, dead ends or hidden recovery. The deliberately ambiguous negative control must be rejected rather than guessed through.
