# BDD journey catalogue template

Use rules, examples, and questions to clarify the affected requirements.

## J01: `<short stakeholder goal>`

- **Requirement IDs:** `<linked IDs>`
- **Stakeholder or actor:** `<person, role, or system>`
- **Starting context:** `<relevant state and conditions>`

### Rules

- `<business or product rule>`
- `<boundary or invariant>`

### Examples

#### Normal

- Given `<starting condition>`
- When `<action or event>`
- Then `<observable outcome>`

#### Boundary

- Given `<boundary condition>`
- When `<action or event>`
- Then `<observable outcome>`

#### Failure or recovery

- Given `<starting condition>`
- When `<controlled failure or unavailable dependency>`
- Then `<visible behaviour, retained state, recovery, and cleanup>`

### Questions

- `<unresolved question, responsible owner, and resolution path>`

### Evidence links

- TDD or deterministic checks: `<IDs>`
- Playwright journey: `<ID or N/A>`
- Midscene question: `<ID, validation status, or N/A>`
- Diagnostics and recovery exercise: `<ID or N/A; include disclosure and opt-out journeys>`
