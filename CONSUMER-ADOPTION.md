# Consumer adoption specification

Status: supported/manual adoption slice verified for the documented local synthetic path. Non-executing inspection and package-script reporting retain bounded independent acceptance. Explicit command planning has bounded independent review with the empty-target finding closed; the accepted source retains its 36/36 implementation result. The [operator walkthrough](WALKTHROUGH.md) starts with the current existing-literal-gate route: inspect, explicit plan/reviewed diff, confirm, then separately authorised native checks. It separately preserves historical public scaffolding and manual native-test adoption in a synthetic stdlib-Python Git project, including success, deliberate failure and restoration. The walkthrough and raw results have been checked; broader consumer readiness remains unproven.

## Consumer capability state map

Historical evidence is bounded to its recorded fixtures or consumers. Source presence alone does not establish a current pass.

| Consumer capability | Current state | Proposed contract |
| --- | --- | --- |
| Inspect configuration without changing files | Independently accepted file-derived inspection without version executables; bounded synthetic scope | Broader instruction/manifest inspection and component mapping remain proposed |
| Retain native tools and commands per component | Unexecuted package script declarations at root and one recognised Vite frontend; broader mapping remains manual | Evidence-based component mapping; no shipped native-runner discovery |
| Resolve detected, configured and LLM proposals | Person/LLM explicit `--command` selections share a read-only preview; supplied provenance remains unverified | One reviewable mapping path, including a no-LLM route |
| Review changes before applying them | Bounded independently reviewed literal gate diff preview and fingerprint-confirmed application with stale-byte/selection refusal; blind local use passed | Broader file-owner support remains proposed |
| Reapply without losing existing work | Reviewed literal gate application appends missing commands with exact deduplication; accepted baseline repeat use required manual backup relocation; content-derived retained backups have bounded independent and fresh blind acceptance. Selected scaffolding preserved. `GATE.md` overwritten | Broader reapplication remains proposed |
| Run gates and expose failures | Synthetic Python native unittest and manually selected generated gate both passed; deliberate assertion produced gate exit 1; restored fixture passed | Native dependency installation, production builds and applicable journeys remain consumer-specific and unproven here |
| Prove isolation, restart and closure; bind evidence | Manual procedures; templates require adaptation | Separate assertions, cleanup, counts, skips, revision and scope |

### Mixed Go backend and React frontend example

Proposed mapping for a synthetic repository: `backend/go.mod` owns a Go API and `frontend/package.json` owns a React/Vite UI using npm. After inspecting its documented commands, retain `go test ./...` and `go build ./cmd/api` in `backend/`; retain `npm ci`, `npm test` and `npm run build` in `frontend/`. Map its documented browser command and service prerequisites separately. These are desired mappings, not commands discovered or verified by this generator.

Current heuristics look for Go markers at the repository root, so this backend is missed. Vite detection can find `frontend/`, but generates Bun-based commands; it does not infer the established npm workflow or the API entrypoint. The report now displays literal scripts declared in root `package.json` and the single recognised Vite frontend, with each owning directory. It does not select npm/Bun or verify those declarations; generated commands remain unchanged. The explicit plan can preview these supplied backend/frontend selections for manual adaptation. General component mapping and native-runner discovery remain proposed.

## Product outcome

Help a developer or coding agent adopt a reliable development workflow without rebuilding their project around this framework. Inspect the repository, explain gaps, reuse working tools, apply a reviewed set of changes, and demonstrate the resulting setup through its ordinary entrypoints.

The product is both readable guidance and code implementing that guidance. Manual, explicitly configured and LLM-assisted adoption must follow the same rules. Neither generated files nor a green summary alone establish readiness.

## Who it serves

- A developer bringing an existing project into a repeatable development workflow.
- A coding agent doing the same work under the repository owner's authority.
- A maintainer inspecting exactly what would change before allowing adoption.

A new project may use supported defaults. An established project keeps sound equivalents. Do not replace a working test runner merely because detection does not understand it.

## Consumer journey (eventual contract)

The following describes the intended broader product. Only the supported/manual scope in [WALKTHROUGH.md](WALKTHROUGH.md) is delivered by this milestone; automatic mapping, broader application and full consumer setup verification below remain proposed.

### 1. Inspect without executing project code

Read repository instructions, manifests, lockfiles, documented commands and relevant configuration. Report observed facts separately from inferred mappings. Do not install packages, run hooks, import configuration code, start services or read credential values during detection.

Identify components, not just a single repository-wide language. For each component, locate its directory, runtime, package manager, lockfile, install/test/build/dev commands and relevant browser or persistence boundary. A Go backend and React frontend require distinct mappings plus any shared integration checks.

Missing, contradictory or unsupported evidence produces an explicit unresolved item. A filename match does not prove a command works.

### 2. Resolve the mapping

Use three cooperating routes:

- Detection proposes mappings from concrete repository evidence.
- Explicit user configuration supplies or overrides mappings with a recorded reason.
- An optional LLM proposes mappings for ambiguous layouts, citing source paths and explaining uncertainty.

All routes produce the same reviewable adoption plan. No separate LLM-only installation path. The LLM may propose intent-sensitive decisions, not silently authorize them. Without an LLM the manual/configured route remains usable.

Ask only for a consequential decision that cannot safely be inferred. Prefer outcome wording: which application must work, whether remote services are allowed, and what must remain untouched. Do not require consumers to learn our internal taxonomy.

### 3. Review one concrete plan

Show, for each applicable role and component:

- existing capability and evidence path;
- keep, add, adapt, not applicable or unresolved;
- native command and working directory where applicable;
- exact proposed file changes and their reason;
- prerequisite, authority and verification requirements;
- demonstrated versus merely detected support.

Reuse existing configuration and documentation. Extend repository instructions without replacing unrelated content. Never silently overwrite dirty or conflicting files. Repeated adoption must not accumulate duplicate sections or repin tools without review.

The plan is a view over the adoption mapping, not a second progress database or assurance ledger. Begin with existing project configuration and the current adoption map; add a machine-readable format only if a demonstrated implementation seam requires one.

### 4. Apply the approved coherent batch

Recheck relevant file state before writing. Preserve the prior state through an appropriate reversible mechanism. Apply the bounded approved changes rather than requesting permission separately for every file. Package installation, service activation, network exposure, credentials and publication remain separately governed protected actions.

Prefer native commands and established FOSS tools. Do not introduce a general-purpose build system, custom dependency installer, background owner or scheduler. Keep the existing dependency-free Python adoption core unless a separately justified change is approved.

### 5. Demonstrate the actual setup

Configuration detection is not acceptance. Exercise supported ordinary install, test and production-build entrypoints. Where applicable, exercise browser journeys against the real build, synthetic state persistence across normal restart, environment isolation and owned-service closure.

Record discovered/passed/failed/skipped counts and distinguish historical from new skips. Assertion outcome and cleanup outcome remain separate. Missing prerequisites, zero discovered tests and unrun required checks cannot pass. A safe synthetic test environment must still provide explicitly declared dependencies to nested workers.

Bind the result to the evaluated source and environment. Say exactly which scope passed; leave other platforms, live providers, deployment and unexercised functionality unproven. Setup readiness is not ticket compliance or proof of user benefit.

### 6. Hand over daily use

Leave concise repository-local instructions: normal commands, working directories, safety boundaries and known gaps. Daily change verification follows brief → examples → focused TDD → relevant checks → real journey → exact-candidate review. Do not reinstall or fully requalify an unchanged setup for every change.

## Prose/code agreement

Each automated rule needs a documented behaviour, implementation location and owning test. Each promised behaviour must be implemented, explicitly manual or explicitly unsupported. Documentation examples must agree with actual command dispatch and results.

Consumer-facing statuses distinguish: detected, proposed, applied, verified, failed and unproven. Installation must not produce a readiness claim before verification. Do not collapse them into a single green badge.

## Evidence and current gaps

These are different evidence classes, not one aggregate product acceptance:

- Existing prose: README.md, ADOPT.md, STACK.md and quality-gate/README.md already separate setup readiness from change acceptance and require reuse of native tools.
- Existing code: the Python adoption scaffolding and generated gate commands exist. Its documentation explicitly says it is not native-runner discovery. Defaults such as Python pytest and Go ./cmd/server require review/adaptation. General component mapping and the unified detected/configured/LLM plan are proposed, not demonstrated.
- Kept retained evidence: the record attributes local acceptance of `150b7c9` to native checks, production build, bounded browser coverage and restart/closure evidence. Its referenced final independent review and raw acceptance evidence are missing from the current corpus. Preserve that attribution without declaring failure. This is project experience, not universal installer acceptance.
- CFA retained evidence: `c73a1ec` and [field lessons](research/field-lessons.md) describe earlier runtime repairs. The later isolated setup recorded 3,217 discovered, 3,194 passed, 22 skipped and one failed, exit 1. Eighteen skips were historical and four additional conditional host-integration skips. A nested launch lacked Chromium before reaching its intended assertion; sanitization failure is not established. Fourteen conformance passes cover offline Dallas/static inputs with synthetic basemap bytes, not live providers or the full release wrapper. Setup remains partial.
- Toybox retained acceptance: independent review accepted `4a74757d8d68c919f54f2790cd44b6eae90d8e1e63cd5fafb8dd95cc02529954` for owned dependencies, a cold-copy installation and a bounded no-recording journey. Root and cold-copy suites each recorded 80 passes and zero failures across 11 files; frozen mismatch was refused. Source applications and compatible preinstalled Chromium remained prerequisites. This does not prove automatic discovery, fresh-machine browser provisioning or the full consumer journey.
- Unsupported/unproven: arbitrary monorepos, automatic native-runner discovery, general plan application, platform portability and LLM mapping correctness. Do not market these as shipped.

Private evidence locations are maintainer provenance, not required consumer dependencies. Public claims need concise scope and revision references without leaking private records.

## Implementation inventory and first candidate

Read-only source inventory separates what exists from the desired product:

- `quality-gate/adopt.py` uses `detect_go`, `detect_bun`, `detect_python` and `detect_rust` through `detect_all`. Audit disables executable version probes; installation retains them for pins. Audit labels marker evidence, unprobed versions, unverified command defaults and unproven readiness.
- `detect_vite` searches a fixed list of frontend directories; `detect_playwright` finds configuration paths. These heuristics are not general component or native-command discovery.
- `ADAPTERS` contains command defaults, including pytest and Go `./cmd/server`. They must not be presented as discovered project commands.
- The first bounded repair uses the existing report and detector path without a new dependency or format. `AdoptionContracts.test_audit_uses_file_evidence_without_subprocesses` covers nine synthetic fixtures; `test_public_doctor_does_not_invoke_path_version_wrappers` checks the public entrypoint and unchanged fixture bytes; `test_install_preserves_explicit_version_probing_and_pins` separately characterises installation pins.
- The initial inventory found no explicit/LLM mapping input or reviewed plan/apply boundary. The explicit command planning successor below supplies the bounded preview and manual application path.

First-candidate acceptance: audit completes with tool subprocess calls forbidden, a public doctor invocation never executes a synthetic PATH wrapper, repository bytes remain unchanged, output accurately labels evidence and uncertainty, and installation version pins remain independently covered.

The earlier baseline attempt stopped in Safe Chain before discovery. James subsequently approved a project-only exception for local tests and the verifier using the verified absolute Python, without installs or sandbox changes. The resumed baseline discovered and passed 12 tests; all three verifier checks passed. Before implementation, the nine-fixture audit test recorded seven assertion failures and two errors caused by attempted version probes, and the public doctor test failed because its PATH wrappers ran. The separate installation-pin characterisation passed. All three focused tests now pass, including fixture byte preservation. The prior candidate subsequently received bounded independent acceptance for non-executing inspection and installation pins; it is not full consumer installation acceptance. Existing Vite file-handle ResourceWarnings remain outside this repair.

## Package-script reporting successor

Implemented scope: audit/public doctor read root `package.json` and the single
frontend selected by the existing fixed-directory Vite detector, deduplicating root.
The existing text report labels source manifest/path, script name, literal command
and working directory relative to the target. These are unexecuted declarations/candidates,
not verified native commands or a selected package manager. JSON escaping preserves
command text while keeping newlines/control characters inert. No script or config
is executed/imported; no general monorepo scanning or shell interpretation is added.

An absent root manifest is informational and root package-script discovery is not
applicable unless the existing Vite detector already identified it as expected.
Missing expected manifests (including a present path disappearing before reading),
present unreadable manifests, invalid JSON/encoding, nonobject manifest/scripts and
nonstring script values are unresolved discovery and contribute to gaps. Valid
siblings remain reported. Missing or empty scripts are allowed. Marker matches,
including the legacy Bun match on `package.json`, do not establish Bun as fact.
Installation probing, generated defaults and gate generation remain unchanged.

Eight added `test_script_*` tests cover mixed Go-root/React-Vite declarations,
custom names, deduplication, absent/empty scripts, malformed/wrong types,
valid siblings, invalid encoding, control characters, unchanged fixture bytes,
forbidden subprocesses and generation compatibility. The accepted candidate's
seven hashes matched before changes, allowing reuse of its retained 15/15 baseline.
The F1 repair adds four owner-layer compatibility regressions for pure Go, pure
Python, neutral no-JavaScript and nested-only frontend layouts, plus two boundary
tests retaining missing-expected and present-unreadable gaps. The original
missing-root false-gap assertion was corrected; malformed checks remain.
Independent F1 closure passed 11/11 bounded checks with zero forbidden attempts
and preserved fixture bytes, closing the missing-root false-gap finding. Its retained
29/29 implementation baseline remains attributed to the implementer. General mapping
and automatic application remain proposed. Declaration reporting leaves consumer
setup readiness unproven.

## Explicit command planning successor

Implemented `adopt.py plan TARGET --command TASK DIRECTORY COMMAND` accepts repeatable
explicit selections for the existing six gate tasks. Person and LLM use the same
arguments after inspecting doctor output. Provenance is explicitly supplied/unverified.
The planner preserves custom invocations and repeated task command order, supports
partial selection and real internal directories beyond detector coverage, and emits
ordered adoption-map rows plus entries for the existing generated `COMMANDS` dict.
Remaining manual tasks and all stack roles stay visible.

The planner validates every selection before printing the snippet. No selection,
invalid arity/task, blank command, missing target/directory, absolute paths, traversal
and outside symlinks produce exit 2. Display strings are escaped, command literals
round-trip, and `shlex` quotes directory-scoped subshells that gate the whole command.
Planning executes no command, probes no versions, invokes no Git subprocess and
leaves target files unchanged. Existing target gate/config files stay inert.

Selected lists replace only selected `COMMANDS` entries after human/agent review
preserving all existing required checks. Update the authoritative adoption map,
review the diff and execute ordinary gate tasks only with target authority.
The original default retains manual application. The opt-in successor below adds
bounded literal gate application. Automatic declaration matching, native-runner
inference, broader application and general role mapping remain unimplemented.
The [walkthrough](quality-gate/README.md#explicit-command-plan) defines the exact syntax and application boundary.

Six owner-layer tests cover deterministic no-LLM preview, mixed components,
ordered lists, partial plans, custom invocations, validation, escaping and planning
preservation with subprocesses forbidden and poison target files. Manual application
in an owned synthetic fixture exercises ordinary generated `gate.py test` for
directories/order, fail-first stopping and whole-command directory gating. This
candidate subsequently received bounded independent review; the empty-target
finding was repaired and independently closed. The accepted repaired source retains
36/36 implementation tests without a new full-suite run for this prose milestone.
The seven accepted predecessor hashes matched before editing, permitting reuse
of its retained 29/29 baseline. Broader consumer readiness remains unproven.

## Reviewed literal gate application candidate

A person and an LLM use the same existing selectors, with an explicit mode before
selections. `plan TARGET --preview-gate --command TASK DIRECTORY COMMAND` reads
existing `gate.py` as inert UTF-8 text and emits a display-only line-oriented
unified diff for direct review, the retained authoritative JSON-escaped exact diff
for byte copying after decoding, and a deterministic SHA-256 confirmation.
Display lines have a `| ` prefix, readable ASCII quotes/hunk layout, doubled
backslashes and visible escapes for controls and non-ASCII; they are not literal
source to paste/apply. Empty display explicitly reports no changes. `plan TARGET --apply-gate FINGERPRINT
--command TASK DIRECTORY COMMAND` requires that prior value with identical target
and selections. The original plain plan remains read-only and paste-ready.

The bounded AST editor accepts one simple module-level literal `COMMANDS`
dictionary with known task-string keys and list-of-string values. Selected tasks
must exist. Missing rendered commands append after existing commands with exact
deduplication. Unselected entries and unrelated bytes survive. A manual decision
owns removal of unsuitable defaults and applicability of required checks.

The fingerprint binds canonical target, original bytes/mode, ordered selections
and resulting bytes. Changed bytes or selectors refuse. A changing apply retains
an original-byte SHA-256/mode-named backup per distinct original revision/mode,
reusing only an exact matching regular nonsymlink file. Historical and legacy
backups remain intact without pruning. It exclusively prepares one fixed temporary
file, flushes prepared files and rechecks original content/identity/mode immediately
before atomic replacement. Backup mismatch or temporary collision refuses with
manual recovery guidance. Fresh confirmed no-change application writes nothing. The
[operator contract](quality-gate/README.md#reviewed-gate-application-contract)
details file names, source-shape restrictions and recovery. One-writer operation
and ordinary stale-edit refusal are the demonstrated scope. Hostile concurrent
writers and every filesystem race remain outside the guarantee.

Reviewed-application regressions cover this capability in synthetic local fixtures, including real
generated gate execution of one native unittest, assertion failure and retained
fail-first behaviour. Preview/application guard target execution, subprocesses
and sockets. The previously accepted owning suite passed 49 tests; bounded independent source
review and binding-refusal closure passed. No target task runs during
preview/application. Broader consumer readiness, platforms, runner inference and
research boundaries retain their prior limits.

A fresh blind consumer received only public product files, a user goal and a
synthetic Python project. It preserved the original required check, added two
native tests, demonstrated failure/restoration and made a second reviewed update.
The product copy remained unchanged. The supervising parent checked those results
and independently proved the old required check could still fail the gate before
the native tests. That attempt exposed backup relocation, escaped-diff inspection
and an unnecessary generic installation suggestion as usability findings.

The content-derived backup successor passed 53 owning tests and bounded independent
review. A fresh blind consumer then completed three changing applications without
moving recovery history, preserved its legacy backup and three new backups, and
demonstrated native failure/restoration and successful final test/verify tasks.
Parent checks matched the unchanged public snapshot, original project bytes/modes,
recovery backups, raw failure exits and actual final task execution. Backup
housekeeping is resolved within this local scope. Blanket installer advice, walkthrough route ambiguity and escaped-diff inspection motivated the bounded repairs below.

## Existing-gate guidance repair

The public guidance contract retains inspection exits, gap counts, unresolved declarations and unproven readiness. Existing `gate.py` routes to explicit selections, supported-source diff review and confirmation without reinstalling; doctor does not parse it. Existing Makefiles retain native recipes, with missing targets added manually where applicable. Completeness still uses all six existing target-name markers, not mere Makefile presence. Only a missing gate with a matched adapter gets optional scaffolding advice, with Git/write-authority and overwrite limits; no adapter routes to manual adoption. Commands use shell quoting inside JSON display strings. No native command is selected or executed automatically and service applicability remains a manual assessment.

The `test_guidance_*` public-entrypoint regressions own this contract, including malformed declarations with retained valid siblings, complete/incomplete Makefiles, no-adapter existing gates and space/quote/control-character paths. The walkthrough puts the supported existing-gate path first and labels historical manual transfer and optional scaffolding separately. This bounded guidance does not expand supported source shapes or make a new readiness or broader mapping claim.

The final owning suite passed 59 tests. Bounded independent review reproduced eight diagnostic cases and the reviewed native pass/failure/restoration route. A fresh blind consumer followed inspection, explicit review and confirmed application without an installer or product repair, correctly distinguished inspection completion from readiness, and completed failure/restoration plus a later update. Parent checks matched the frozen public files, original project bytes/modes, retained recovery history and actual final test/verify results. These remain local synthetic observations.

## Direct preview review

The display-only line-oriented diff passed 63 owning tests and bounded independent
review: 17 public runs and seven deterministic rendering cases preserved exact JSON,
fingerprints, confirmation framing and inert control text. A fresh blind consumer
reviewed two changes directly without a JSON decoder pipeline, preserved the old
required check and recovery history, demonstrated assertion failure/restoration,
and executed a later multiline syntax check. Parent checks matched the frozen public
files, original project bytes/modes, backups, raw failure exits and final native tasks.
Multiline string escapes and nested quotes still required the public legend and
Python quoting knowledge; this is not proof of novice comprehension or arbitrary
terminal security. Exact JSON remains authoritative for byte copying.

## Remaining backlog (ranked)

These are remaining product gaps, not implemented capabilities.

1. **Repeat-use ergonomics:** backups, existing-gate guidance and direct diff review now have bounded acceptance. Multiline/quoted Python string interpretation remains manual; do not treat decoder-free review as general novice usability. Literal `gate.py` application has bounded acceptance; other file owners and general application remain proposed. Scaffold generation writes directly and overwrites `GATE.md`.
2. **Evidence-based component and native-runner mapping:** general monorepo detection, automatic declaration matching and detected/configured/LLM convergence remain proposed. Today commands are explicitly supplied and reviewed; limited marker/script reporting does not infer a runner.
3. **Broader consumer verification:** actual dependency installation, production builds, applicable browser/restart/isolation checks and required stack-role evidence need separately authorised consumer runs. This stdlib fixture proves only the documented local path and failure propagation.
4. **Portability:** other platforms and shells remain unsupported/unproven by this run. Review generated commands for the admitted environment before execution; no automatic portability guarantee exists.

Existing research boundaries and missing Kept final-review/raw-evidence sources remain unchanged. No new empirical or universal tool-superiority claim is introduced. The walkthrough's documented local path is verified within its stated limits.

## Bounded delivery sequence

1. Reconcile retained CFA/Kept/Toybox findings into the rule/evidence map. Identify contradictions and missing acceptance evidence; do not repeat unchanged green suites.
2. Inventory current generator behaviour against this consumer contract. Classify each behaviour as existing/demonstrated, existing/unproven, missing or intentionally manual. Inspect implementation before choosing a new format or dependency.
3. Select the smallest missing consumer behaviour with an observable acceptance scenario. Search existing repository and maintained FOSS mechanisms before custom implementation. Keep the implementation behind meaningful owner-layer RED/GREEN tests.
4. Update the applicable prose and implementation together; run focused regressions during work, required broader gates at the coherent candidate boundary, and one bounded independent review. Repair concrete blockers and rerun affected evidence without starting an open-ended programme.
5. Demonstrate that candidate on explicitly admitted consumers and report exact scope. No product repository mutation, service activation or publication is implied by this specification.

## Acceptance scenarios for the eventual adoption product

- Existing working native commands are retained and run from their owning directories.
- A mixed-stack repository produces component-specific mappings, not one guessed global runner.
- An unsupported layout produces an actionable unresolved mapping, not fabricated defaults or a pass.
- Explicit configuration and an LLM proposal enter the same validated mapping path as detection.
- A no-LLM/manual path completes every supported required adoption step.
- A plan identifies file changes before writes and refuses a conflicting post-plan edit.
- Reapplication preserves user changes and does not duplicate generated instructions.
- Failed build, failed test, unexpected skip, missing browser dependency or cleanup failure remains visible with nonzero failure at its owning gate.
- Detection and successful generation never masquerade as executed setup verification.

These scenarios define proposed observable behaviour. They are not claims that the current code already passes them.
