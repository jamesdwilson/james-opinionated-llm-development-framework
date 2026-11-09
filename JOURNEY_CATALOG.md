# Journey catalog v1

**State:** authorised_for_local_implementation on 2026-11-08

This catalog extrapolates the already accepted `Wash dishes` approval idea into a broader standalone full-stack methodology test. It remains synthetic and local-only.

## J01 — Create an approval-required task

**Story:** As Alex, I can create `Wash dishes` and choose an outcome-labelled rule so I know another household member must approve completion.

**Happy path:** Open the corrected UI → enter the task → choose `Require another person's approval` → create → see `Open` with the visible rule.

**Acceptance:**
- No `Core` or `Required` terminology.
- One required policy decision, expressed by practical consequence.
- Created task identity and creator are visible.
- Reload preserves the task.

**Failure boundary:** Empty or whitespace-only title is rejected without losing the form state.

**Friction budget:** at most 4 primary interactions, 1 required decision, 0 unexplained terms, 0 context switches, 0 dead ends.

## J02 — Complete and independently approve

**Story:** As Alex, I can request completion; as Sam, I can approve it; the person requesting completion cannot approve their own request.

**Happy path:** Alex marks complete → status becomes `Waiting for Sam's approval` → switch to Sam → approve → status becomes `Complete`.

**Acceptance:**
- While Alex is the requester, the UI names Sam as required approver and exposes no actionable self-approval control. A real same-origin API request separately proves the existing 403 enforcement.
- Independence is relative to the completion requester, not the original creator. If Sam requests completion of an Alex-created task, Alex may approve it; Sam may not.
- Sam can approve once.
- Repeated approval is idempotent and does not duplicate history.
- State transitions are exact and deterministic.

**Friction budget:** at most 4 primary interactions after creation, 0 unexplained terms, 1 justified actor switch, 0 dead ends.

## J03 — Persistence and provenance

**Story:** After reload or server reopen, I can see the task's current state and a truthful event trail.

**Happy path:** Complete J02 → reload page → inspect history.

**Acceptance:**
- Task and status survive document reload and database reopen.
- History records creation, completion request and approval in order.
- Each event names its actual actor and time.
- No client-only state is accepted as persistence evidence.

**Friction budget:** at most 2 interactions, 0 new decisions, 0 unexplained terms.

## J04 — Invalid input and recovery

**Story:** If I submit an invalid task title, I understand the problem, retain control and can correct it without restarting.

**Happy path:** Submit whitespace-only title → see field-associated error → enter valid title → create successfully.

**Acceptance:**
- Server and UI enforce the same validation contract.
- Error is announced and associated with the title field.
- Focus returns to the invalid field.
- Valid title input clears stale validation and aria-invalid before resubmission; a corrected submission succeeds without reloading.

**Friction budget:** 1 recovery step, 0 context switches, 0 dead ends.

## J05 — Ambiguous taxonomy negative control

**Story:** As a cold first-time user, I refuse to guess between unexplained `Core` and `Required` options.

**Happy path:** Enter the task → reach the required ambiguous choice → stop without selecting either.

**Acceptance:**
- Deterministic evidence proves no option was selected and Continue/Create remained unavailable.
- Midscene returns `RED / stopped_at_unclear_choice` with the visible terminology as evidence.
- No hidden glossary or leading defect description is supplied.

## J06 — Whole-journey North-Star review

**Story:** A bounded reviewer judges whether the corrected journey looks and behaves like a trustworthy household task flow.

**Happy path:** Observe J01–J03 across representative frames → review against North Star v1.

**Acceptance:**
- Structured `GREEN`, `RED` or `UNCLEAR` output.
- Evidence, friction, contradictions and unvisited scope are explicit.
- A model result cannot override any deterministic failure.
- J06 requires GREEN/completed_goal and empty visible contradictions. Reload/persistence are proved by deterministic Playwright on the unchanged candidate; truthful nonvisual unvisitedScope does not fail the visible review.

## Risk-based execution matrix

- Mobile 390×844, Alex, corrected, pointer: J01 + J03.
- Desktop 1280×800, Alex→Sam, corrected, keyboard/pointer: J02 + J04.
- Mobile 390×844, cold user, ambiguous: J05.
- Desktop 1280×800, North-Star-informed reviewer, corrected: J06.

## Trace chain

`North Star v1 → J01–J06 → rules/examples above → accessible UI names/states → focused domain/API tests → Playwright journeys → bounded Midscene reviews → exact-candidate evidence`
