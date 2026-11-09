# Acceptance contract template

## Candidate

- **Identity:** `<verified clean commit or defined working-tree fingerprint>`
- **Profile:** Lean | Standard | High Assurance
- **Accepted journey set:** `<path or IDs>`

A commit identifies the candidate after a clean-working-tree check. A dirty candidate fingerprints the fully materialised relevant tree. Each canonical record contains a path, file state, type, executable mode, bytes or symlink target, with a deletion marker for every relevant base path now absent. Sort records by path and length-prefix each field. Generated reports and evidence outputs stay outside the candidate input set.

## Evidence hierarchy

Every applicable required check must pass. When two pieces of evidence address the same claim, use this order:

1. security and permission checks;
2. domain, persistence, and API checks;
3. deterministic browser journeys;
4. failure, recovery, and cleanup evidence;
5. dependency and provenance checks;
6. bounded model judgement;
7. prose summaries.

The higher-ranked evidence controls that shared claim. Any required failure blocks acceptance.

## Required checks

| Check ID | Requirement IDs | Claim | Authority | Method | Procedure or command | Expected result | Evidence |
|---|---|---|---|---|---|---|---|
| C01 | `<R-001, Q-001>` | `<claim>` | `<owner or test layer>` | test | `<command>` | `<result>` | `<path>` |
| V01 | `<Q-002>` | `<claim>` | `<reviewer or stakeholder>` | inspection | `<procedure>` | `<recorded observation>` | `<report path>` |

## Model-review boundary

**Allowed questions:**

- `<question about visible clarity, hierarchy, ambiguity, or friction>`

**Result schema:**

```json
{
  "verdict": "GREEN | RED | UNCLEAR",
  "stopped_at": "stable label",
  "evidence": ["visible fact"],
  "reason": "concise explanation"
}
```

`RED` or `UNCLEAR` on a required product journey stops acceptance. Expected `RED` on an isolated negative control passes that control; `GREEN` or `UNCLEAR` fails calibration.

## Failure and recovery cases

| ID | Injected condition | Expected boundary | Visible result | Retained state | Cleanup proof |
|---|---|---|---|---|---|
| F01 | `<condition>` | `<boundary>` | `<result>` | `<state>` | `<proof>` |

## Closure

Acceptance requires:

- exact candidate identity;
- complete required-check inventory;
- expected results, with exits and counts where the method is executable;
- intact evidence;
- resolved blockers;
- independent review where the profile requires it.

For the same candidate and required check, the latest completed attempt controls. A repaired failure remains in history while the changed candidate receives a fresh acceptance run.
