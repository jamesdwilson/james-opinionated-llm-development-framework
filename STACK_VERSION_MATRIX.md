# Entire test-stack version matrix

Status date: 2026-11-08

## Verdict

The lab is **not on every latest public release**. Bun is current and is now the sole JavaScript runtime. JavaScript dependencies remain on the newest versions admitted by the host's supply-chain freeze, while Bugsink and dotenv remain behind. Moving only to the latest public JavaScript packages would **not clear the dependency audit**.

The previously evaluated Node 26.13.0 target is no longer part of the lab execution plan.[1]

The host npm policy is currently `before = Sun Nov 01 2026 13:02:01 CST`. Packages published later are unavailable to installation unless that security control is deliberately advanced.

## Matrix

| Component | Installed / selected | Latest public | Current assessment |
| --- | --- | --- | --- |
| Bun | 1.4.4 | 1.4.4 | Current sole JavaScript runtime. Native `node:sqlite` compatibility passed persistence/API tests; Bun deterministic tests passed 30/30 twice and Bun-driven Playwright passed 6/6 twice.[13][14][15] |
| npm | 11.12.1 | 12.2.2 | Latest is a major update and was published after the npm freeze. Keep blocked until the quarantine date is deliberately advanced and compatibility is checked.[3] |
| Python | 3.14.2 | 3.14.10 | Behind on security/bug-fix patches. Python 3.14.10 is the current 3.14 release and includes security fixes.[2] |
| pip | 25.3 | 26.3 | Behind. Upgrade with the Python runtime, not independently inside the protected shared Bugsink environment.[4] |
| Bugsink | 2.1.2 | 2.6.3 | Materially behind. Latest isolated probe passed Django system checks, both database migrations and creation of a project-bound capability token.[8][9] |
| Django used by Bugsink | 5.2.13 | 5.2.19 in the Bugsink 2.6.3 environment | Managed by Bugsink's pinned dependency set; upgrade through Bugsink rather than independently overriding it. |
| Playwright | 1.63.0 | 1.65.0 | Installed version is the newest admitted by the Nov 1 npm freeze. Latest public release remains quarantined.[5] |
| Playwright Chromium | 156.0.8078.4, revision 1248 | Coupled to Playwright 1.65.0 | Do not update the browser independently; validate the browser bundle with the Playwright upgrade. |
| Midscene Web | 1.17.4 | 1.17.7 | Installed version is the newest admitted by the Nov 1 npm freeze. Latest public release remains quarantined and is still within the current audit's affected ranges.[6] |
| dotenv | 16.4.5 | 18.0.9 | Behind, but 18.0.9 is old enough for the current npm freeze and declares Node >=12. It can be upgraded in the lab candidate.[7] |
| Midscene BDD runner | Native `runGherkinScenario()` already available through installed `@midscene/web` | `@midscene/test` 1.17.7 is available separately | Do not add another runner yet. The existing Playwright integration already supplies the required Gherkin API. |
| Midscene model | SIWC `gpt-6-sol`, `balance`, provider reasoning `low` | `gpt-6.1-sol` is the newer OpenAI reasoning model | Latest is not automatically best here. Midscene's own BDD guide currently recommends `gpt-6-sol` with `balance`; keep it until the approved BDD suite can compare repeatability and diagnostic quality.[10][11] |
| Implementation / hostile-review model | `gpt-6-astra`, medium | Role-specific internal route | Keep. It serves a different reasoning role and should not be replaced merely to make every role use the same model. |

## Executed compatibility findings

### Bun compatibility probe

A checksum-verified official Bun 1.4.4 binary is now installed and pinned by the lab. Bun migrated the existing `package-lock.json` into `bun.lock` while retaining the exact direct versions admitted by the package quarantine.[14][15]

This supersedes the initial Bun 1.3.9 probe, which lacked the `node:sqlite` compatibility required by the lab.[12]

Bun 1.4.4 implements the `node:sqlite` API used by this lab. The unchanged persistence and API paths pass under Bun. The final exact candidate passed 30/30 deterministic tests twice and 6/6 Playwright journeys twice with Playwright forced to execute under Bun. An initial complete Bun browser run also exposed and allowed repair of a genuine asynchronous application-readiness race in J04.

Bun's audit command still finds the same vulnerable Midscene dependency graph, expressed as 13 advisories across six packages rather than npm's package-level 15 high / 1 moderate count. Bun consumes the frozen migrated lock and is not being used to bypass the November 1 package quarantine.

### Latest npm packages

An isolated package-lock probe attempted:

- `@playwright/test` 1.65.0
- `@midscene/web` 1.17.7
- `dotenv` 18.0.9

Installation was correctly refused because Playwright and Midscene were published after the configured Nov 1 package cutoff.

A second isolated probe used the latest currently admitted package set:

- `@playwright/test` 1.63.0
- `@midscene/web` 1.17.4
- `dotenv` 18.0.9

Result: **15 high and 1 moderate vulnerability remained**. Testing npm's suggested Midscene 1.12.5 downgrade produced the same count. Therefore neither “upgrade everything” nor the suggested downgrade is a demonstrated security repair.

The current audit attributes all sixteen findings to the Midscene dependency graph, including vulnerable versions or ranges involving `js-yaml`, `sharp`, `uuid`, `zod`, Puppeteer/proxy/archive dependencies and Midscene's own packages. Its ranges include Midscene 1.17.7, so merely waiting for the latest currently published Midscene release will not clear the gate.

### Bugsink 2.6.3

A fresh isolated Python environment installed Bugsink 2.6.3 and its own pinned dependencies. Against fresh lab-only SQLite state it passed:

- Django system check;
- default database migrations;
- Snappea database migrations;
- fresh Team and Project creation;
- project-bound API token creation;
- `projects:read`, `issues:read` and `events:read` capability assignment;
- temporary-state cleanup.

This is the strongest immediate upgrade candidate. Bugsink added project-bound tokens in the 2.6 line, which can replace the lab's custom global-token read-only boundary rather than merely carrying that limitation forward.[9]

## Recommended upgrade order

1. **Bugsink 2.1.2 → 2.6.3**, adapting the isolated harness to native project-bound capability tokens. Re-run migration, canary ingestion/readback, recovery and every cleanup mutation.
2. **Python 3.14.2 → 3.14.10** and **pip 25.3 → 26.3** for the new isolated Bugsink environment. Do not mutate the protected existing port-8100 environment.
3. **dotenv 16.4.5 → 18.0.9** with focused config-loading tests.
4. Keep **Playwright 1.63.0** and **Midscene 1.17.4** until the package quarantine is deliberately advanced. Then test 1.65.0/1.17.7 in an isolated candidate, but do not expect that pair to clear the audit.
5. Treat the Midscene dependency advisories as an upstream/remediation decision: wait for a fixed Midscene dependency graph, or isolate and pin reviewed overrides only after a compatibility spike. Do not force an audit fix.
6. Keep `gpt-6-sol`/`balance` for the initial approved Midscene BDD calibration. Compare `gpt-6.1-sol` only as a bounded model experiment with the same scenarios, fixtures and deterministic twins.

## Current acceptance effect

Hostile findings 1–7 are repaired and parent-verified:

- Bun 30/30 twice;
- Chromium 6/6;
- real isolated Bugsink canary passed;
- port 8100 identity remained unchanged;
- finalized scan passed with zero findings or limit violations.

Fresh exact-candidate Midscene J05/J06 evidence passed twice. Full closure is blocked only by unresolved Midscene dependency security: Bun reports 10 high and 3 moderate advisories across six packages.

## Sources

[1] https://nodejs.org/en/blog/release/v26.13.0
[2] https://www.python.org/downloads/release/python-31410
[3] https://registry.npmjs.org/npm/latest
[4] https://pypi.org/project/pip
[5] https://registry.npmjs.org/@playwright/test/latest
[6] https://registry.npmjs.org/@midscene/web/latest
[7] https://registry.npmjs.org/dotenv/latest
[8] https://pypi.org/project/bugsink
[9] https://www.bugsink.com/docs/changelog
[10] https://midscenejs.com/advanced/bdd-style-scripts-with-gherkin.html
[11] https://developers.openai.com/api/docs/models/gpt-6.1-sol
[12] https://bun.com/blog/bun-v1.3.9
[13] https://bun.com/guides/test/playwright
[14] https://bun.com/docs/pm/lockfile
[15] https://github.com/oven-sh/bun/releases/tag/bun-v1.4.4
