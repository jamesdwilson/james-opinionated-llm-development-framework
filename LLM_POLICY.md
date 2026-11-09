# Lab role policy

The executable policy is `llm-policy.json`; `test/policy.test.mjs` validates it and the exact package command. This policy records the supplied research; no new Midscene run is needed for configuration verification.

| Role | Route/model | Reasoning |
| --- | --- | --- |
| Domain, persistence, API, Playwright state/permissions/provenance/reload/accessibility mechanics, Bugsink, dependency audit, evidence integrity, cleanup | no LLM | none |
| J05/J06 rendered-UX reviewer | SIWC `gpt-6-sol`, family `gpt-6` | Midscene `balance`, provider `low` |
| Implementation/repair executor | `openai-codex`, `gpt-6-astra` | `medium` |
| Independent hostile code/security/acceptance reviewer | `openai-codex`, `gpt-6-astra` | `medium`; read-only, independent of writer |

Playwright drives deterministic interaction. Midscene supplies bounded visible-UX judgments. `UNCLEAR` cannot pass; Midscene GREEN cannot overrule deterministic failure. No Gemini. No default `aiAct`, API-key route, or deprecated `codex://app-server` route.

Escalate one layer at a time (Midscene `deepThink` OR provider `medium`), only after a repeatable miss or a genuinely long/branching journey. Autonomous high-level journeys are reserved for calibration, material UX changes, and exact release candidates.

Research supplied for this batch: fast/balance/deepThink agreed on the material RED/GREEN pair. Balance used 11 calls/276,516 tokens versus deepThink's 18/~410k and fast's 11/269,039. SIWC used ~93k per pair (~66% fewer than deprecated balance). Reviewer-only used 2 calls/35,124 tokens versus full AI interaction's 5/111,778. These support balance/low, SIWC, and Playwright-driven bounded review.

Run `npm run test:stack` for deterministic candidate, explicit real Bugsink gate, and dependency audit. Audit failure blocks full acceptance. Existing accepted Midscene evidence is preserved, not rerun for every commit. Parent independent verification must use `gpt-6-astra` via `openai-codex` with medium reasoning and `--skip-git-repo-check` (this lab has no Git repository).
