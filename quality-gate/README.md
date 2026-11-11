# The quality gate

Two words this toolkit uses precisely, borrowed from the standards world:

- A **qualified environment** is a development setup you can trust to tell
  you the truth: locked dependencies, honest tests, isolated configuration,
  safe startup. (Avionics calls this tool qualification, DO-330.) The gate
  below is how a project earns it, and qualification is always scoped:
  "qualified for local macOS development" says nothing about Linux or
  production.
- A **validated candidate** is a change that provably does what its brief
  says. (IEEE V&V: verified against the spec, validated against the real
  goal, with traceability from brief to test.) The rest of this framework's
  chain owns that side. Qualification comes first, because goal-alignment
  evidence from an untrustworthy environment is worthless.

This directory is the quality gate: the prose standard, an installer, a
read-only checker, and templates. It was proven on a real project (Kept,
November 2026: 334 web tests, 121 of 125 browser journeys passing with zero
failures, a restart smoke and an independent review).

## Use it

You need Python 3.9 or newer. That is the only requirement, and you probably
already have it: Python ships with macOS's developer tools and every desktop
Linux, comes preinstalled on GitHub's runners, and is the most-used language
among people working with AI agents. If not, one install from python.org or
your package manager sorts it.

```bash
# doctor: is this project's environment still qualified? Read-only,
# changes nothing, run it as often as you like.
python3 quality-gate/doctor /path/to/project

# install: install the safe pieces, get your remaining steps in GATE.md.
python3 quality-gate/install /path/to/project

# Also add an optional CI workflow:
python3 quality-gate/install /path/to/project --ci
```

Install needs a git repository, because every change it makes is meant to be
read as an ordinary `git diff` before you commit it. doctor needs nothing
but the project itself.

## What you get: the contract

Six commands, generated for your stack as a `gate.py` in your project:

```
python3 gate.py install            locked dependencies only, frozen install, no lifecycle scripts
python3 gate.py test-e2e-install   browser test dependencies
python3 gate.py verify             module integrity, clean diff, pinned tool versions
python3 gate.py test               the complete native test suite
python3 gate.py build              the real production artifacts
python3 gate.py test-e2e           build once, run the browser suites
```

Already have a Makefile, Taskfile or npm scripts with the same steps? That
counts. The shape is the contract, not the tool you run it with.

## The rules

Every rule here exists because its absence caused a real, observed defect:

- **Lockfile required.** A frozen flag alone does not reject a missing
  lockfile. Check for the file.
- **Isolated environment.** Explicit child environment, `--no-env-file` on
  Bun routes, `envDir: false` in Vite configs, and a planted-sentinel test
  proving stray `.env` files cannot change results.
- **Synthetic state only.** Dedicated test databases, uploads and runtime
  directories. Never household config or provider credentials.
- **Loopback only, strict ports, no server reuse.** Fail if a port is taken;
  never adopt someone else's service.
- **The browser runner owns its services**, and they demonstrably close
  afterwards.
- **Cleanup never gates tests.** A missing cleanup helper cannot fail a
  passing test.
- **Safe `dev` startup.** Never delete the local database on a normal start.
  State survives a normal stop and restart.
- **No manufactured green.** No broad excludes or new skips. Existing product
  coverage is the floor.

## Qualifying

A project's environment is qualified when one reviewed Git candidate, from a
fresh checkout with nothing copied over, passes:

1. The full chain above: clean, no unexpected failure, no new skip, no
   missing tracked input, no environment leakage.
2. The start/restart smoke (see `templates/restart-smoke.md`).
3. One bounded independent review of the diff and the results. One review.
   Do not invent more rounds.

Then claim exactly what you proved. "Qualified for local macOS development"
says nothing about Linux, containers, deployment or AI services, and that's
fine: those stay visible and non-blocking until a feature needs them. CI is
likewise your call (`--ci`), not a requirement.

## What the tool does, and never does

It detects your stack, writes only missing files, and writes `GATE.md`
with your remaining steps. Three rules always hold: **never overwrite a
project file, never delete anything, no hidden machinery.** No transactions,
journals, receipts or rollback protocols; an earlier version of this
programme built all of that, and the machinery generated more work than it
saved. Plain files, reviewed like any other change.

What it cannot safely automate (safe `dev` commands, env-isolation wiring,
the smoke, the acceptance run itself) becomes numbered instructions in
`GATE.md` for you or your agent.

## Do it by hand instead

Happy to. The tool is a convenience, not a requirement. Here is exactly what
it does, precise enough to follow step for step.

**doctor only looks:**

1. Notes the operating system.
2. Detects toolchains by marker files: `go.mod` is Go; `bun.lock` or
   `package.json` is Bun; `pyproject.toml`, `requirements.txt`, `setup.py`
   or `Pipfile` is Python; `Cargo.toml` is Rust; `package.json` beside a
   `vite.config.*` (in `web/`, `frontend/`, `ui/`, `app/`, `apps/web/`,
   `client/` or the root) is a Vite frontend, and Vitest if that file
   mentions it; any `playwright*.config.*` within three directory levels
   is Playwright.
3. Reads the versions of whatever it found.
4. Checks the contract: a `gate.py`, or a Makefile with the six steps,
   and whether `dev` startup ever deletes a database.
5. Checks whether every Vite config sets `envDir: false`.
6. Prints the report and verdict. Changes nothing.

**install writes only missing, reviewable files:**

1. Refuses unless the target is a git repository with a matched toolchain.
2. If no contract file exists, generates `gate.py`: each toolchain
   contributes its native commands to the six steps, plus a pin for each
   tool version found. Existing contract files are never modified; gaps
   become written instructions.
3. With `--ci` and no workflows directory, writes one Ubuntu workflow
   running the same chain, pinned to the detected versions.
4. With a Vite + Vitest frontend, copies the env-isolation test template
   if absent.
5. Writes `GATE.md`: what was found, what was installed, your numbered
   remaining steps.
6. Stops. Everything is visible as an ordinary `git diff`.

## Extend it

The core knows the contract; adapters know toolchains. Adapters for Go, Bun,
Python and Rust ship today, plus Vite/Vitest and Playwright as framework
adapters that compose with any of them. A mixed project (Go backend, Bun
workspace, Vite frontend) gets one composed `gate.py`, each line from its
own adapter. Add a stack by adding one entry to the registry in `adopt.py`:

```python
{
    "name": "mytool",
    "detect": detect_mytool,           # facts dict, or None when absent
    "install": ["mytool fetch --locked"],
    "verify": ["mytool verify"],
    "test":   ["mytool test"],
    "build":  ["mytool build --release"],
    "pin":    lambda f: [...],          # version pin tuples (name, command, want)
    "guidance": {"topic": "remainder text for GATE.md"},
}
```

## Not required yet

Historical assurance, containers, AI services, deployment, supply-chain
attestation and hostile-host threat models all wait until a feature actually
needs them. They are not part of qualification.

## Proof and sources

Kept, November 2026: candidate `150b7c9`, 334 web tests, 125 browser tests
discovered / 121 passed / 4 pre-existing skips / 0 failures, restart smoke,
independent review PASS. The full reasoning, including the machinery that
was tried and retired, is in `Golden-Implementation-Playbook-2026-11-11.md`
(companion to the Golden Development Contract, 2026-11-10; both predate this
vocabulary but say the same things).
