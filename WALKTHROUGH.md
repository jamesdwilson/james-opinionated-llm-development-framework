# Consumer walkthrough

Follow this authorised local path: inspect → explicit plan → reviewed scaffolding/manual application → native test → scoped result. A person and an LLM use the same CLI. A plan supplies commands; it neither discovers the correct runner nor authorises execution.

This path was exercised on a new local Git project with a Python marker, an adoption map and one stdlib arithmetic test, on macOS with Python 3.14.5. Public scaffolding, manual application, passing native tests, deliberate assertion failure and restoration were exercised. This is bounded synthetic evidence, not general consumer or platform acceptance. The accepted source's prior 36/36 suite was retained without rerunning it.

## 1. Inspect

Read the target's instructions, working-tree state, documented native commands and their bodies. Use [ADOPT.md](ADOPT.md) to maintain an authoritative adoption map covering every [stack role](STACK.md), with reasons for keep, add, N/A, blocked or not run.

This example needs an existing trusted Python 3.9+ interpreter with stdlib `unittest`, Git and a POSIX shell. Select the target's intended test interpreter and use it consistently. No dependencies need installation for this stdlib fixture. These assignments are placeholders for existing local checkouts, not observed output:

```sh
FRAMEWORK=/path/to/framework
TARGET=/path/to/local-git-project
PYTHON=/path/to/selected/python3
```

From the framework checkout:

```sh
"$PYTHON" -B "$FRAMEWORK/quality-gate/doctor" "$TARGET"
```

`doctor` inspects file evidence without version executables. The exercised fixture exited 0, matched Python via `pyproject.toml`, reported `version=unprobed`, seven gap groups, unverified defaults and readiness unproven. Exit 0 means inspection completed. Package-script declarations are unexecuted candidates, limited to root and one recognised Vite frontend.

## 2. Supply an explicit plan

For a target whose reviewed native test is stdlib discovery from its root:

```sh
"$PYTHON" -B "$FRAMEWORK/quality-gate/adopt.py" plan "$TARGET" \
  --command test . "$PYTHON -B -I -m unittest discover -s tests -v"
```

Here the selected interpreter path must contain no spaces or shell metacharacters; otherwise quote it inside the command string for the target shell. The planner preserves supplied shell text; review the actual emitted entry.

The exercised plan exited 0 and preserved target bytes. It emitted a proposed/unexecuted `test` row and an entry for the existing `COMMANDS` dictionary, with remaining tasks and all manual roles visible. It executed no target command. Person and LLM pass identical `--command TASK DIRECTORY COMMAND` arguments. Repeat selections to retain ordered checks; merge all required existing checks before replacing a selected list. Partial plans are supported. See the [six task names and validation contract](quality-gate/README.md#explicit-command-plan). Invalid selections exit 2 without a snippet.

## 3. Authorised scaffolding and manual application

If missing scaffolding is authorised, inspect the preservation/overwrite rules below, then run:

```sh
"$PYTHON" -B "$FRAMEWORK/quality-gate/install" "$TARGET"
```

This public `install` writes scaffolding; it does not install project dependencies. It probes available matched tools and checks Git. The exercised Python-only fixture constrained probes to trusted local Python and Git, used no `--ci`, and exited 0, reporting `gate.py(generated:python)` and `GATE.md`. Generated **`gate.py install` can install dependencies and was not run**.

Existing `gate.py` and Makefile are preserved; `GATE.md` is overwritten on every scaffold run. Keep manual notes in the adoption map. Without scaffold authority, use the [manual procedure](quality-gate/README.md#do-it-by-hand) and an existing native owner; that alternative was not exercised here.

Read `gate.py` and `GATE.md`. Manually paste the reviewed plan's selected entry into the existing `COMMANDS` dictionary, replacing only that task's list. In this fixture the emitted unittest list replaced the default pytest `test` list; every other entry stayed intact. There were no other required fixture tests. Existing consumers must merge all their required checks. For a Makefile or another owner, transfer reviewed selections into its native recipes. Automatic application and conflict rechecking are unimplemented.

Update the adoption map from proposed to applied. Review `git status --short`, tracked diffs and complete new-file contents: `git diff` omits untracked scaffolding. The fixture's WALK-1 requirement linked the arithmetic pass/failure scenario to its native command. Browser/UX and service work were N/A with reasons, dependency review recorded stdlib-only scope, and candidate evidence/review remained manual. Generic generated instructions do not waive a real product's applicable requirements.

## 4. Run the native test and gate

With target execution authority, run from the target root:

```sh
cd "$TARGET"
"$PYTHON" -B -I -m unittest discover -s tests -v
"$PYTHON" -B gate.py test
```

Both exercised commands exited 0: one test ran, one passed, zero failed, zero skipped. The gate ran the selected native command from the selected root directory. Zero discovered tests would not support the claim.

For the **synthetic fixture only**, the test was `self.assertEqual(2 + 2, 4)`. Change the expected value to `5`, run the same `gate.py test` command and record the result separately. The actual assertion was `4 != 5`: one test ran, one failed, zero skipped, gate exit 1. The gate also printed a `CalledProcessError` traceback. Restore the expected value to `4` and rerun the gate before finishing. The restored run exited 0 with one passing test. This demonstrates failure propagation, not implementation TDD or product coverage.

## 5. Report the truthful result

Record the candidate/tree identity, environment, commands, working directories, exits, counts, raw evidence locations and restored final state. Bind the deliberate failure to its distinct fixture bytes. Mark the selected test verified only after execution.

This run supports local scaffolding and manual native-test adoption for this fixture. No generated dependency-install, verify, build or browser task ran. Service/restart, live providers, deployment and cross-platform acceptance remain unproven. Gate test does not itself prove environment isolation.

Supported today: file-derived inspection, bounded package declarations, validated explicit preview, scaffolding and manual transfer into existing commands. Role disposition, authorisation, preserving checks, diff review and result interpretation remain manual. Automatic application, general runner/component or monorepo detection, automatic LLM mapping and portable shell behaviour remain proposed or unproven. See the [ranked remaining backlog](CONSUMER-ADOPTION.md#remaining-backlog-ranked). The documented path and raw results have been checked; no universal readiness claim follows from this handover.
