# Consumer walkthrough

For an existing supported literal `gate.py`, follow this current route: inspect → explicit plan and reviewed diff → confirm → separately authorised native check → scoped result. No scaffold installation is needed, even when no adapter matches. A person and an LLM use the same CLI. A plan supplies commands; it neither discovers the correct runner nor authorises execution.

## 1. Inspect

Read the target's instructions, working-tree state, documented native commands and their bodies. Use [ADOPT.md](ADOPT.md) to maintain an authoritative adoption map covering every [stack role](STACK.md), with reasons for keep, add, N/A, blocked or not run.

This example needs an existing trusted Python 3.9+ interpreter with stdlib `unittest`, an existing supported literal gate and a POSIX shell. Git helps review the diff but is not required by doctor or plan/application. Select the target's intended test interpreter and use it consistently. No dependencies need installation for this stdlib fixture. These assignments are placeholders for existing local checkouts, not observed output:

```sh
FRAMEWORK=/path/to/framework
TARGET=/path/to/local-git-project
PYTHON=/path/to/selected/python3
```

From the framework checkout:

```sh
"$PYTHON" -B "$FRAMEWORK/quality-gate/doctor" "$TARGET"
```

`doctor` inspects file evidence without version executables. Exit 0 means inspection completed; readiness remains unproven. An existing `gate.py` is only a file-presence observation: doctor does not parse its commands or verify source shape. Package-script declarations are unexecuted candidates, limited to root and one recognised Vite frontend. Keep every reported gap for applicability and safety assessment in the adoption map; adding commands does not resolve all gaps or decide whether services are required.

Optional top-level `packageManager` evidence from those same manifests quotes
exact declared/unverified intent and its owning directory. It does not select or
verify a manager or command; legacy adapters/scaffold defaults are not chosen
from it. Absent/unusable optional declarations add no gaps. Inspect the documented
native commands before supplying the explicit plan. See the
[metadata boundary](quality-gate/README.md#optional-package-manager-declaration-evidence).

Keep an existing Makefile or other native owner. A Makefile is reported complete only when all six named task markers are present; that does not verify recipes. Use the manual route below for those owners or unsupported gate source. If no gate exists, consider the separate scaffolding alternative below only when an adapter matches. No adapter match is needed for explicit planning or supported existing-gate application.

For a mixed layout, doctor additionally reports an immediate-child regular
nonsymlink `backend/go.mod` with owning directory `backend` as unverified file
presence. The root-only adapter summary can still say no Go adapter matched.
Read the supplied `backend/README.md` (or the target's command authority), then
use its exact documented command with `--command test backend 'go test ./...'`
only if that is the reviewed declaration. Use the same selection in plain plan,
preview and confirmed application below. Do not run the gate merely to inspect
the mapping: this slice leaves Go commands unexecuted and unverified. Existing
checks stay first and later changing applications retain their backups. See the
[scope contract](quality-gate/README.md#immediate-child-go-marker-evidence): deeper,
linked, hidden and dependency/build layouts are uninspected, and metadata failures
remain unknown. This is directory evidence, not Go test success or native readiness.

## 2. Supply an explicit plan

For a target whose reviewed native test is stdlib discovery from its root:

```sh
"$PYTHON" -B "$FRAMEWORK/quality-gate/adopt.py" plan "$TARGET" \
  --command test . "$PYTHON -B -I -m unittest discover -s tests -v"
```

Here the selected interpreter path must contain no spaces or shell metacharacters; otherwise quote it inside the command string for the target shell. The planner preserves supplied shell text; review the actual emitted entry.

The exercised plan exited 0 and preserved target bytes. It emitted a proposed/unexecuted `test` row and an entry for the existing `COMMANDS` dictionary, with remaining tasks and all manual roles visible. It executed no target command. Person and LLM pass identical `--command TASK DIRECTORY COMMAND` arguments. Repeat selections to retain ordered checks. Reviewed application appends missing commands after existing checks; manual replacement must merge every required existing check. Partial plans are supported. See the [six task names and validation contract](quality-gate/README.md#explicit-command-plan). Invalid selections exit 2 without a snippet.

## 3. Review the diff and confirm application

Review the current checks and the plain plan, then preview the additive change with the same
selection interface. The mode option follows TARGET and precedes selections.

```sh
"$PYTHON" -B "$FRAMEWORK/quality-gate/adopt.py" plan "$TARGET" --preview-gate \
  --command test . "$PYTHON -B -I -m unittest discover -s tests -v"
"$PYTHON" -B "$FRAMEWORK/quality-gate/adopt.py" plan "$TARGET" --apply-gate FINGERPRINT \
  --command test . "$PYTHON -B -I -m unittest discover -s tests -v"
```

Replace `FINGERPRINT` with the exact `Confirmation SHA256` value after reviewing
the display-only, line-oriented unified diff directly. Each diff line has a `| `
prefix; doubled backslashes and visible Unicode escapes keep controls inert. Do
not paste/apply this display as source. For exact byte copying, decode the
contiguous authoritative JSON diff block instead. An empty display says no changes. The
second command requires identical selectors and unchanged gate bytes/mode.
Existing selected commands stay first. A default pytest command would therefore
still run before the appended unittest command. Removing an unsuitable default
requires a separate explicit manual decision and a fresh preview.

Only an existing supported simple literal `COMMANDS` dictionary is edited. This
creates no new gate, runs no task and supplies no readiness certificate. The
changing apply preserves original bytes/mode in
`gate.py.reviewed-backup-sha256-HEX-mode-MMMM` (original-byte SHA-256 and four-digit
octal mode). Historical backups, including the legacy fixed backup, stay intact.
Later changes need no backup relocation. Exact matching regular nonsymlink backups
may be reused; mismatches refuse. Exclusive `gate.py.reviewed-tmp` preparation
and the final original identity/content/mode check precede atomic replacement.
An existing temporary path refuses: inspect the target and reported recovery
paths, preserve evidence and manually restore verified bytes/mode or relocate the
incomplete temporary file before a fresh preview/retry. No automatic pruning occurs.
After successful application, fresh preview has an empty diff and confirmed
no-change apply writes nothing. See the [full bounded contract and recovery
limits](quality-gate/README.md#reviewed-gate-application-contract).

Update the authoritative adoption map and review the resulting diff and new recovery files. Keep applicability, declarations, prerequisites and safety gaps unresolved until separately assessed. This route preserves existing checks and requires no installer.

## 4. Run the native test and gate

With target execution authority, run from the target root:

```sh
cd "$TARGET"
"$PYTHON" -B -I -m unittest discover -s tests -v
"$PYTHON" -B gate.py test
```

Record actual counts and exits. The gate runs its existing checks before the appended native command from the selected directory. Zero discovered tests would not support the claim.

For the **synthetic fixture only**, the test was `self.assertEqual(2 + 2, 4)`. Change the expected value to `5`, run the same `gate.py test` command and record the result separately. Expect `4 != 5`, one failed test and a nonzero gate exit. A generated gate also prints a `CalledProcessError` traceback. Restore the expected value to `4` and rerun the gate before finishing; record the restored passing result. This demonstrates failure propagation, not implementation TDD or product coverage.

## 5. Report the truthful result

Record the candidate/tree identity, environment, commands, working directories, exits, counts, raw evidence locations and restored final state. Bind the deliberate failure to its distinct fixture bytes. Mark the selected test verified only after execution.

Supported today: file-derived inspection, bounded package declarations, explicit command planning and optional reviewed application to a supported existing literal gate. Manual transfer and adapter-based scaffolding remain alternatives below. Role disposition, authorisation, preserving checks, diff review and result interpretation remain manual. Native-runner inference, general file-owner application, automatic LLM mapping, portable shell behaviour and complete environment readiness remain unproven. See the [capability map and backlog](CONSUMER-ADOPTION.md#consumer-capability-state-map).

## Alternatives and historical evidence

### Optional scaffolding when no gate exists

If no gate exists, an adapter matches, Git is available and scaffold writes are authorised, inspect the preservation/overwrite rules below before running:

```sh
"$PYTHON" -B "$FRAMEWORK/quality-gate/install" "$TARGET"
```

This public `install` writes scaffolding; it does not install project dependencies. It probes available matched tools and checks Git. The exercised Python-only fixture constrained probes to trusted local Python and Git, used no `--ci`, and exited 0, reporting `gate.py(generated:python)` and `GATE.md`. Generated **`gate.py install` can install dependencies and was not run**.

Existing `gate.py` and Makefile are preserved; `GATE.md` is overwritten on every scaffold run. Keep manual notes in the adoption map. Without scaffold authority, use the [manual procedure](quality-gate/README.md#do-it-by-hand) and an existing native owner; that alternative was not exercised here.

### Historical manual transfer and no-LLM alternative

The earlier synthetic walkthrough used this manual route. It remains available without an LLM, as do explicit planning and reviewed application. Read the existing gate (and `GATE.md` if generated). Manually paste the reviewed plan's selected entry into the existing `COMMANDS` dictionary, replacing only that task's list. In this fixture the emitted unittest list replaced the default pytest `test` list; every other entry stayed intact. There were no other required fixture tests. Existing consumers must merge all their required checks. For a Makefile or another owner, transfer reviewed selections into its native recipes. That historical manual replacement remains an explicit fixture decision. The
reviewed application route above appends commands while retaining every existing check.

Update the adoption map from proposed to applied. Review `git status --short`, tracked diffs and complete new-file contents: `git diff` omits untracked scaffolding. The fixture's WALK-1 requirement linked the arithmetic pass/failure scenario to its native command. Browser/UX and service work were N/A with reasons, dependency review recorded stdlib-only scope, and candidate evidence/review remained manual. Generic generated instructions do not waive a real product's applicable requirements.

This path was exercised on a new local Git project with a Python marker, an adoption map and one stdlib arithmetic test, on macOS with Python 3.14.5. Public scaffolding, manual application, passing native tests, deliberate assertion failure and restoration were exercised. This is bounded synthetic evidence, not general consumer or platform acceptance. The accepted source's prior 36/36 suite was retained without rerunning it.

The historical fixture's direct native and gate tests each passed one test with zero skips. Changing the expected value from `4` to `5` produced `4 != 5`, one failure and gate exit 1; restoring `4` passed. This supports that local scaffolding/manual-transfer path and failure propagation. No generated dependency-install, verify, build or browser task ran. Services, restart, live providers, deployment, isolation and cross-platform acceptance remained unproven.
