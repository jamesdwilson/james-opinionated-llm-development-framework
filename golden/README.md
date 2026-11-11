# Golden: the development gate

A project is **golden** when a named subject satisfies a named policy profile,
for a stated purpose, on current, complete, trustworthy evidence. Never merely
"the last command returned zero".

This directory is the practical standard: prose, an adoption script and
templates. Running the script gets a project as far toward golden as
automation reasonably reaches, then writes the exact remaining steps for a
human or LLM into the project's `GOLDEN.md`.

Field-validated: this standard is what the Kept project was actually accepted
against (November 2026), after an expensive detour proved what does not work.
The hard-won version of the lesson:

> The goal is a reliable development environment, not a framework
> distribution, provenance or attestation product. Adopt golden as one
> ordinary, reviewed Git candidate verified by native commands. Add an
> abstraction only when a demonstrated native-path defect requires it.

## Architecture: universal core, adapters at the edges

The gate itself is language-agnostic. The ideals are not Go ideals or
TypeScript ideals: locked dependencies, honest tests, isolated environments,
synthetic state, safe startup and reviewed evidence apply to every stack and
every operating system. So the tool is built in two layers.

**The universal core** (`adopt.py`, stdlib-only Python 3, single file, no
dependencies) knows the contract shape, the safety properties, the acceptance
gate, the audit report and the GOLDEN.md remainder. It runs identically on
macOS, Linux and Windows. It never learns anything about your language.

**Adapters** know one toolchain each: how to detect it, pin its version and
fill its native commands into the contract. Shipping adapters cover Go, Bun,
Python and Rust toolchains, plus Vite/Vitest and Playwright as
framework adapters that compose with any of them. Adding a stack means adding
one entry to the adapter registry in `adopt.py`:

```python
{
    "name": "mytool",
    "detect": detect_mytool,           # facts dict, or None when absent
    "install": ["mytool fetch --locked"],
    "verify": ["mytool verify"],
    "test":   ["mytool test"],
    "build":  ["mytool build --release"],
    "pin":    lambda f: [...],          # Makefile lines pinning the version
    "guidance": {"topic": "remainder text for GOLDEN.md"},
}
```

A project using several stacks gets one composed Makefile: Go backend, Bun
workspace and Vite frontend land in the same thin contract, each through its
own adapter. That is how the gate spreads without the ideals forking per
language.

## What the script deliberately is not

`adopt.py` detects, writes plain files and writes a status document. It has
no transactions, journals, capsules, receipts, ownership manifests or
rollback protocols. Kept built all of those; they generated a day of proof
work about themselves and proved nothing a developer needed. Everything the
script changes appears as an ordinary git diff, reviewed like any other
change.

## The thin native contract

One repository, one reviewed Git candidate, one thin Make interface, the
native toolchain. No new framework engine, installer, daemon or proof
database.

```
make install            require the lockfile; go mod download; bun --no-env-file install --frozen-lockfile --ignore-scripts
make test-e2e-install   playwright install chromium (CI adds --with-deps)
make verify             go mod verify; git diff --check; pinned tool versions
make test               go test ./... -count=1; go vet ./...; production tsc; full frontend tests; env/lifecycle regressions
make build              server + CLI binaries; tsc -b; vite build
make test-e2e           build once, then the established Playwright suite chain
```

Projects without Go or without a browser drop the matching lines. The shape
is the contract, not the letter.

## Non-negotiable properties

Each exists because its absence caused a real, observed defect:

- **Lockfile required.** A frozen flag alone does not reject a missing
  lockfile. Test for the file explicitly.
- **Environment isolation.** Explicit child environment, `--no-env-file` on
  Bun routes, `envDir: false` in Vite configs, and a planted-sentinel
  regression proving ambient `.env` files cannot alter results.
- **Synthetic state only.** Dedicated synthetic databases, uploads and runtime
  directories. Never household configuration or provider credentials.
- **Loopback only, strict ports, no server reuse.** Fail if a required port
  is occupied; never adopt a foreign service.
- **The browser runner owns service startup and shutdown**, and owned
  services demonstrably close afterwards.
- **Cleanup never gates tests.** A missing cleanup helper cannot fail a
  passing test.
- **`make dev` is safe and ordinary.** Never delete the local database on
  normal startup; state survives a normal stop and restart.
- **No broad excludes or skips to manufacture green.** Existing product
  coverage is the floor.

## The acceptance gate

Development is golden when one reviewed Git candidate passes, from a fresh
checkout with no copied `node_modules`, build output or runtime state:

1. `make install && make test-e2e-install && make verify && make test && make test-e2e` —
   clean pass, no unexpected failure, no new skip, no missing tracked input,
   no ambient environment leakage.
2. The start/restart persistence smoke (see `templates/golden-smoke.md`).
3. One bounded independent review of the exact diff and the actual results.
   One review. Do not invent further acceptance rounds.

CI is a per-project decision (`install --ci`), not a universal gate. Claim
only the scope actually demonstrated: "golden for local macOS development"
says nothing about Linux, containers, deployment or AI services. Unclaimed
scopes stay visible and non-blocking.

## Using the tool

**All you need is Python 3.9+.** We chose one runtime on purpose so the tool
stays small, readable and easy to trust. Happily, it's the friendliest
possible choice: Python is used by 58% of all developers (Stack Overflow
2026) and is the most-used language among people working with AI agents
(39%), it arrives with macOS's developer tools, ships in every desktop
Linux, and comes preinstalled on GitHub's Ubuntu, macOS and Windows runners.
Chances are you already have it. If a machine doesn't yet, one install from
python.org or your package manager sorts it out in a minute, and from then on
there's just one implementation to read, run and maintain.

```bash
# Read-only status report:
python3 golden/adopt.py audit /path/to/project

# Install what is safely installable and write GOLDEN.md:
python3 golden/adopt.py install /path/to/project

# Additionally install the optional CI workflow:
python3 golden/adopt.py install /path/to/project --ci
```

The tool never overwrites a project file and never modifies an existing
Makefile. What it cannot safely automate (safe `dev` targets, env-isolation
wiring, the smoke, the acceptance run itself) lands in `GOLDEN.md` as
numbered, exact instructions for a human or LLM.

## And if you'd rather not run it

That's completely fine. The tool is a convenience, not a requirement, and
everything it does is small enough to do by hand. Here is exactly what it
does, in plain language, precise enough for a person or an LLM to follow
step for step.

**Audit mode changes nothing. It only looks.**

1. Notes the operating system.
2. Checks which toolchains are present, one simple test each: a `go.mod`
   means Go; a `bun.lock` or `package.json` means Bun; a `pyproject.toml`,
   `requirements.txt`, `setup.py` or `Pipfile` means Python; a `Cargo.toml`
   means Rust; a `package.json` next to a `vite.config.*` (in `web/`,
   `frontend/`, `ui/`, `app/`, `apps/web/`, `client/` or the root) means a
   Vite frontend, and if that package file mentions Vitest, Vitest too;
   any `playwright*.config.*` within three directory levels means Playwright.
3. Reads the versions of the tools it found, when they are installed.
4. Checks whether a `Makefile` exists and whether it defines `install`,
   `verify`, `test`, `build`, `test-e2e` and `test-e2e-install`, and whether
   a `dev` target exists that never deletes a database.
5. Checks whether every Vite config sets `envDir: false`.
6. Prints all of that as a report with a verdict, and exits.

**Install mode writes only missing, reviewable files.**

1. Refuses unless the target is a git repository with at least one matched
   toolchain. The git boundary is what makes every change reviewable.
2. If there is no `Makefile`, generates one: each matched toolchain
   contributes its native lines (`go mod download`, frozen Bun install,
   `pytest`, `cargo test --locked`, and so on) to the six contract targets,
   plus a version pin for each tool version found on the machine. If a
   `Makefile` already exists, it is never modified; the missing targets
   become written instructions instead.
3. With `--ci` and no existing workflows directory, writes one
   `.github/workflows/native.yml` running the same chain on Ubuntu, pinned
   to the detected versions. CI is always opt-in.
4. With a Vite + Vitest frontend, copies the env-isolation regression
   template (`golden-env-isolation.test.ts`) if no such file exists.
5. Writes `GOLDEN.md` at the project root: what was detected, what was
   installed, and the numbered remaining steps. Those steps are always some
   of: safe `api`/`ui`/`dev` targets (synthetic state, loopback only, strict
   ports, never delete the database), environment isolation wiring, adapting
   the isolation test, the start/restart persistence smoke, and the
   acceptance run itself.
6. Stops. Everything it wrote is visible as an ordinary `git diff`.

**Three rules hold in every mode:** never overwrite a project file, never
delete anything, and no hidden machinery. No transactions, journals,
receipts or rollback protocols, just plain files you can read before you
commit them.

## Deferred, truthfully non-blocking

Historical assurance, container validation, AI-service acceptance, deployment,
supply-chain attestation and hostile-host threat models are each addressed
only when their own claim or feature requires them. They are not development
gates.

## Reference

Kept, November 2026: candidate `150b7c9`, 334 web tests, 125 browser tests
discovered / 121 passed / 4 pre-existing skips / 0 failures, persistence
smoke, independent review PASS. The full reasoning and the retired-machinery
list are in `Golden-Implementation-Playbook-2026-11-11.md` (companion to the
Golden Development Contract, 2026-11-10).
