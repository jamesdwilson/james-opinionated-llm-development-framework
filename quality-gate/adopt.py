#!/usr/bin/env python3
"""quality-gate/adopt.py - audit or install the quality gate in any project.

Universal core + adapter registry. The core knows the quality gate contract shape
(install / verify / test / build / e2e / smoke / review) and how to report it.
Adapters know one toolchain each: how to detect it, pin its version and fill
its native commands into the contract. Operating-system differences are
handled once, in the core.

Design rules (learned the expensive way):
- stdlib only, single file, Python 3.9+. No dependencies to install before
  you can install dependencies.
- Detection, plain file writes and a generated GATE.md. No transactions,
  journals, receipts or rollback machinery. Every change is an ordinary
  git diff reviewed like any other.
- Never overwrite a project file. Never modify an existing Makefile.
  Anything unsafe to automate becomes a numbered instruction instead.

Usage:
  adopt.py audit  TARGET_DIR          read-only status report
  adopt.py install TARGET_DIR [--ci]  install missing safe pieces + GATE.md
"""

import os
import platform
import shutil
import subprocess
import sys
from datetime import datetime, timezone

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


# --------------------------------------------------------------------------
# Adapter registry. To support another toolchain, add one entry here. Each
# adapter provides:
#   name        short identifier
#   detect(t)   -> dict of facts, or None if the toolchain is absent
#   install/verify/test/build/e2e  lists of Makefile recipe lines (optional)
#   pin(facts)  -> list of Makefile recipe lines pinning the tool version
#   guidance    dict of GATE.md remainder text keyed by topic (optional)
# --------------------------------------------------------------------------

def _run(cmd):
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        return out.stdout.strip() or out.stderr.strip()
    except Exception:
        return ""


def _tool_version(cmd):
    return _run(cmd).splitlines()[0] if _run(cmd) else ""


def detect_go(t):
    if not os.path.isfile(os.path.join(t, "go.mod")):
        return None
    ver = _tool_version(["go", "version"]).split(" ")[2] if shutil.which("go") else ""
    return {"version": ver}


def detect_bun(t):
    if not (os.path.isfile(os.path.join(t, "bun.lock")) or os.path.isfile(os.path.join(t, "package.json"))):
        return None
    facts = {"lockfile": os.path.isfile(os.path.join(t, "bun.lock"))}
    facts["version"] = _tool_version(["bun", "--version"]) if shutil.which("bun") else ""
    return facts


def detect_python(t):
    for marker in ("pyproject.toml", "requirements.txt", "setup.py", "Pipfile"):
        if os.path.isfile(os.path.join(t, marker)):
            ver = ""
            if shutil.which("python3"):
                ver = _tool_version(["python3", "--version"]).replace("Python ", "")
            return {"marker": marker, "version": ver,
                    "requirements": os.path.isfile(os.path.join(t, "requirements.txt"))}
    return None


def detect_rust(t):
    if not os.path.isfile(os.path.join(t, "Cargo.toml")):
        return None
    facts = {"lockfile": os.path.isfile(os.path.join(t, "Cargo.lock"))}
    if shutil.which("cargo"):
        facts["version"] = _tool_version(["cargo", "--version"]).split(" ")[1]
    return facts


def detect_vite(t):
    """Frontend framework adapter: Vite + Vitest in a subdirectory or root."""
    for d in ("web", "frontend", "ui", "app", os.path.join("apps", "web"), "client", "."):
        pkg = os.path.join(t, d, "package.json")
        if not os.path.isfile(pkg):
            continue
        try:
            cfgs = [f for f in os.listdir(os.path.join(t, d)) if f.startswith("vite.config.")]
        except OSError:
            cfgs = []
        if not cfgs:
            continue
        try:
            with open(pkg) as fh:
                pkg_text = fh.read()
        except OSError:
            pkg_text = ""
        isolated = any("envDir: false" in open(os.path.join(t, d, c)).read()
                       for c in cfgs
                       if os.path.isfile(os.path.join(t, d, c)))
        return {"dir": d if d != "." else "", "vitest": '"vitest"' in pkg_text, "env_isolated": isolated}
    return None


def detect_playwright(t):
    configs = []
    for root, dirs, files in os.walk(t):
        dirs[:] = [d for d in dirs if d != "node_modules" and not d.startswith(".")]
        if os.path.relpath(root, t).count(os.sep) > 2:
            dirs[:] = []
        configs += [os.path.relpath(os.path.join(root, f), t)
                    for f in files if f.startswith("playwright") and ".config." in f]
    return {"configs": sorted(configs)} if configs else None


ADAPTERS = [
    {
        "name": "go",
        "detect": detect_go,
        "install": ["go mod download"],
        "verify": ["go mod verify"],
        "test": ["go test ./... -count=1", "go vet ./..."],
        "build": ["go build -trimpath -o .gate-local/server ./cmd/server"],
        "build_dirs": [".gate-local"],
        "lockfiles": [],
        "pin": lambda f: [("Go", ["go", "env", "GOVERSION"], f["version"])] if f.get("version") else [],
        "env": {"CGO_ENABLED": "0", "GOTOOLCHAIN": "local",
                "GOENV": "off", "GOWORK": "off", "GOFLAGS": "-mod=readonly"},
    },
    {
        "name": "bun",
        "detect": detect_bun,
        "install": ["bun --no-env-file install --frozen-lockfile --ignore-scripts"],
        "lockfiles": ["bun.lock"],
        "pin": lambda f: [("Bun", ["bun", "--version"], f["version"])] if f.get("version") else [],
        "guidance": {
            "lockfile": "Commit `bun.lock` and keep the explicit lockfile existence check. A frozen flag alone does not reject a missing lockfile.",
        },
    },
    {
        "name": "python",
        "detect": detect_python,
        "install": ["python3 -m pip install -r requirements.txt"],
        "test": ["python3 -m pytest -q"],
        "lockfiles": [],
        "pin": lambda f: [("Python", ["python3", "--version"], "Python %s" % f["version"])] if f.get("version") else [],
        "guidance": {
            "env": "Run tests in a fresh virtualenv with an explicit environment. Do not let ambient shell variables or a developer's site-packages alter results.",
            "install": "Review Python dependency installation against this project's chosen package manager and lock policy. Without requirements.txt, the generated install task deliberately fails until configured; detection of pyproject.toml, setup.py or Pipfile does not identify a safe installation command.",
        },
    },
    {
        "name": "rust",
        "detect": detect_rust,
        "install": ["cargo fetch --locked"],
        "verify": ["cargo verify-project"],
        "test": ["cargo test --locked", "cargo clippy --locked -- -D warnings"],
        "build": ["cargo build --release --locked"],
        "lockfiles": ["Cargo.lock"],
        "pin": lambda f: [("Cargo", ["cargo", "--version"], "cargo %s" % f["version"])] if f.get("version") else [],
    },
]

# Framework/OS adapters below are detection+guidance only; they compose with
# the toolchain adapters above rather than replacing them.


def detect_all(target):
    found = {}
    for a in ADAPTERS:
        facts = a["detect"](target)
        if facts:
            found[a["name"]] = (a, facts)
    return found


def find_makefile_gaps(target):
    path = os.path.join(target, "Makefile")
    if not os.path.isfile(path):
        return None, ["install", "verify", "test", "build", "test-e2e", "test-e2e-install"]
    with open(path) as fh:
        text = fh.read()
    missing = [t for t in ("install", "verify", "test", "build", "test-e2e", "test-e2e-install")
               if ("\n%s:" % t) not in ("\n" + text)]
    return path, missing


def dev_safety(target):
    path = os.path.join(target, "Makefile")
    if not os.path.isfile(path):
        return "unknown"
    with open(path) as fh:
        text = fh.read()
    if "\ndev:" not in "\n" + text:
        return "absent"
    for line in text.splitlines():
        if line.strip().startswith("rm ") and (".db" in line or "sqlite" in line):
            return "unsafe"
    return "present"


def report(target, found, missing, has_gate_py, vite, pw, dev, osname):
    lines = [
        "quality gate report: %s" % target,
        "  operating system:          %s" % osname,
        "  adapters matched:          %s" % (", ".join(sorted(found)) or "none"),
    ]
    for name in sorted(found):
        facts = found[name][1]
        detail = ", ".join("%s=%s" % (k, v) for k, v in facts.items() if v not in (True, ""))
        lines.append("    %-12s %s" % (name, detail or "present"))
    lines += [
        "  vite frontend:             %s" % (vite or "none detected"),
        "  playwright configs:        %s" % (len(pw["configs"]) if pw else 0),
        "  contract:                  %s" % ("gate.py" if has_gate_py else
                                          ("none" if missing[0] is None else
                                           ("Makefile (complete)" if not missing[1]
                                            else "Makefile (missing targets: %s)" % " ".join(missing[1])))),
        "  safe dev targets:          %s" % dev,
    ]
    return lines


GATE_PY_TEMPLATE = '''#!/usr/bin/env python3
"""Quality gate for this project.

Generated by quality-gate/adopt.py. This file IS the contract: read it,
extend it, run it. Requires Python 3.9+ and the project's native toolchains.
Review the generated shell commands for the target platform; generation
does not establish Windows/Linux equivalence or environment readiness.
"""
import os
import subprocess
import sys

ENV = {env}
LOCKFILES = {lockfiles}
PINS = {pins}
BUILD_DIRS = {build_dirs}
COMMANDS = {commands}

ORDER = ["install", "test-e2e-install", "verify", "test", "build", "test-e2e"]


def sh(cmd):
    print("+ %s" % cmd, flush=True)
    subprocess.run(cmd, shell=True, check=True)


def main(argv):
    if len(argv) == 2 and argv[1] in ("--help", "-h"):
        print("usage: python3 gate.py " + "|".join(ORDER))
        return 0
    if len(argv) != 2 or argv[1] not in ORDER:
        print("usage: python3 gate.py " + "|".join(ORDER))
        return 2
    task = argv[1]
    os.environ.update(ENV)
    for d in BUILD_DIRS:
        os.makedirs(d, exist_ok=True)
    if task == "install":
        for lf in LOCKFILES:
            if not os.path.isfile(lf):
                sys.stderr.write("%s is required; refusing unlocked installation\\n" % lf)
                return 1
    if task == "test-e2e":
        main([argv[0], "build"])
    if task == "verify":
        sh("git diff --check")
        for name, cmd, want in PINS:
            try:
                got = subprocess.run(cmd, capture_output=True, text=True).stdout.strip()
            except Exception:
                got = ""
            if got != want:
                sys.stderr.write("%s %s required, found %s\\n" % (name, want, got or "nothing"))
                return 1
    for cmd in COMMANDS.get(task, []):
        sh(cmd)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
'''


def emit_gate_py(found, pw, vite):
    env, lockfiles, pins, build_dirs = {}, [], [], []
    commands = {"install": [], "verify": [], "test": [], "build": [],
                "test-e2e-install": [], "test-e2e": []}
    for _, (a, f) in sorted(found.items()):
        env.update(a.get("env", {}))
        lockfiles += a.get("lockfiles", [])
        pins += a.get("pin", lambda _f: [])(f)
        build_dirs += a.get("build_dirs", [])
        for key in ("install", "verify", "test", "build"):
            if a["name"] == "python" and key == "install" and not f.get("requirements", False):
                commands[key] += ["echo Configure Python dependency installation for this project before running install && exit 1"]
            else:
                commands[key] += a.get(key, [])
    if vite:
        d = vite["dir"] or "."
        commands["test"] += ["bun --no-env-file run --bun --cwd %s tsc --noEmit" % d,
                             "bun --no-env-file run --bun --cwd %s test" % d]
        commands["build"] += ["bun --no-env-file run --bun --cwd %s tsc -b" % d,
                              "bun --no-env-file run --bun --cwd %s vite build" % d]
    if pw:
        e2edir = os.path.dirname(pw["configs"][0]) or "."
        commands["test-e2e-install"] = [
            "bun --no-env-file run --cwd %s playwright install chromium" % e2edir]
        commands["test-e2e"] = ["bun --no-env-file run --cwd %s playwright test" % e2edir]
    else:
        commands["test-e2e-install"] = [
            "echo no playwright config detected; add one, then point this task at it & exit 1"]
        commands["test-e2e"] = ["echo no playwright config detected & exit 1"]
    if not commands["install"]:
        commands["install"] = ["echo no dependency installation detected & exit 1"]
    if not commands["test"]:
        commands["test"] = ["echo no test adapter matched & exit 1"]
    if not commands["build"]:
        commands["build"] = ["echo no build adapter matched & exit 1"]

    def fmt(obj, level):
        import json as _json
        return _json.dumps(obj, indent=4).replace("\n", "\n" + "    " * level)

    return GATE_PY_TEMPLATE.format(
        env=fmt(env, 1), lockfiles=fmt(lockfiles, 0), pins=fmt(pins, 0),
        build_dirs=fmt(build_dirs, 0), commands=fmt(commands, 1))


def main(argv):
    if len(argv) < 3 or argv[1] not in ("audit", "install"):
        sys.stderr.write(__doc__)
        return 2
    mode = argv[1]
    ci = "--ci" in argv[3:]
    target = os.path.abspath(argv[2])
    if not os.path.isdir(target):
        sys.stderr.write("target not found: %s\n" % target)
        return 2

    osname = platform.system()
    found = detect_all(target)
    vite = detect_vite(target)
    pw = detect_playwright(target)
    mf = find_makefile_gaps(target)
    has_gate_py = os.path.isfile(os.path.join(target, "gate.py"))
    dev = dev_safety(target)
    lines = report(target, found, mf, has_gate_py, vite["dir"] if vite else None, pw, dev, osname)

    if mode == "audit":
        print("\n".join(lines))
        gaps = 0 if has_gate_py else len(mf[1])
        gaps += 0 if (vite and vite["env_isolated"]) else (1 if vite else 0)
        gaps += 0 if dev == "present" else 1
        if gaps == 0:
            print("verdict: gate shape present. Run the acceptance gate (fresh checkout chain, "
                  "start/restart smoke, one bounded review) before claiming qualification.")
        else:
            print("verdict: %d gap group(s). Run: quality-gate/install %s" % (gaps, target))
        return 0

    # install mode
    if subprocess.run(["git", "-C", target, "rev-parse", "--is-inside-work-tree"],
                      capture_output=True).returncode != 0:
        sys.stderr.write("refusing: target is not a git repository (review needs a diff boundary)\n")
        return 1
    if not found:
        sys.stderr.write("refusing: no adapter matched; nothing to wire. "
                         "Add an adapter entry in quality-gate/adopt.py for this stack.\n")
        return 1

    installed = []
    if has_gate_py or mf[0] is not None:
        missing_targets = [] if has_gate_py else mf[1]
    else:
        with open(os.path.join(target, "gate.py"), "w") as fh:
            fh.write(emit_gate_py(found, pw, vite))
        installed.append("gate.py(generated:%s)" % "+".join(sorted(found)))
        missing_targets = []

    if ci and not os.path.isdir(os.path.join(target, ".github", "workflows")):
        os.makedirs(os.path.join(target, ".github", "workflows"))
        with open(os.path.join(SCRIPT_DIR, "templates", "native.yml")) as fh:
            wf = fh.read()
        versions = {n: f.get("version", "") for n, (_, f) in found.items()}
        wf = (wf.replace("@GOV@", versions.get("go", "").lstrip("go") or "1.26.0")
                .replace("@BUNV@", versions.get("bun", "") or "1.4.4")
                .replace("@NODEV@", _tool_version(["node", "--version"]).lstrip("v") or "26.0.0"))
        with open(os.path.join(target, ".github", "workflows", "native.yml"), "w") as fh:
            fh.write(wf)
        installed.append(".github/workflows/native.yml")

    if vite and vite["vitest"]:
        dest = os.path.join(target, vite["dir"] or ".", "env-isolation.test.ts")
        if not os.path.isfile(dest):
            shutil.copyfile(os.path.join(SCRIPT_DIR, "templates", "env-isolation.test.ts"), dest)
            installed.append(os.path.relpath(dest, target) + "(template)")

    steps = []
    if missing_targets:
        steps.append("Your existing Makefile was left untouched. Add the six contract steps "
                     "(`install`, `verify`, `test`, `build`, `test-e2e-install`, `test-e2e`) to it, "
                     "or write a `gate.py` by hand from quality-gate/README.md. Missing targets: `%s`. "
                     "Never delete a database in any startup target." % " ".join(missing_targets))
    if dev != "present":
        steps.append("Add safe `api`, `ui` and `dev` commands (extra subcommands in gate.py, or "
                     "Make targets): build and run the server from a persistent synthetic directory, "
                     "bind `127.0.0.1`, use strict ports (fail if occupied, never reuse a foreign "
                     "service), absolute synthetic state paths, no provider credentials or household "
                     "config inherited, and never delete the local database on normal startup.")
    if vite and not vite["env_isolated"]:
        steps.append("Set `envDir: false` in every Vite config in `%s`, run Bun-owned test workers "
                     "with `--no-env-file` (worker execArgv, not just the parent), and keep the "
                     "planted env-isolation regression green." % (vite["dir"] or "."))
    if vite and vite["vitest"]:
        steps.append("Adapt `env-isolation.test.ts` to this project: plant a parent-environment "
                     "sentinel, prove it does not leak into the test worker, prove `.env*` files "
                     "cannot alter results, and prove a deliberately failing assertion really fails.")
    for name in sorted(found):
        for text in found[name][0].get("guidance", {}).values():
            steps.append(text)
    steps.append("Write the start/restart persistence smoke (see quality-gate/templates/restart-smoke.md): "
                 "start the documented dev services on synthetic data, exercise one ordinary journey, "
                 "stop normally, restart, confirm identical persisted state, then confirm every owned "
                 "service and port closes.")
    steps.append("Run the acceptance gate from a fresh checkout (no copied dependencies, build output "
                 "or runtime state): `python3 gate.py install && python3 gate.py test-e2e-install "
                 "&& python3 gate.py verify && python3 gate.py test && python3 gate.py test-e2e` "
                 "(or your Makefile equivalent), then the smoke, then one bounded independent review "
                 "of the diff and results. No unexpected failure, no new skip, no missing tracked input.")

    gate_doc = [
        "# GATE.md", "",
        "Generated by quality-gate/adopt.py on %s. Do not edit; rerun the script."
        % datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "Standard: quality-gate/README.md in james-opinionated-llm-development-framework.", "",
        "## Detected state", "",
    ]
    gate_doc += ["    " + ln for ln in lines]
    gate_doc += ["", "## Installed by the script", "",
               "    " + (" ".join(installed) if installed else "nothing (everything installable was already present)"),
               "", "## Remaining steps for a human or LLM", ""]
    gate_doc += ["%d. %s" % (i + 1, s) for i, s in enumerate(steps)]
    gate_doc += ["", "Qualification is claimed only for the scope actually demonstrated (for example "
                    "\"local development on %s\"). Other platforms, containers, deployment and AI "
                    "services stay unclaimed until each gets its own run." % osname, ""]
    with open(os.path.join(target, "GATE.md"), "w") as fh:
        fh.write("\n".join(gate_doc))

    print("\n".join(lines))
    print("\ninstalled: %s" % (" ".join(installed) if installed else "nothing"))
    print("wrote GATE.md with the remaining steps. Review everything as a normal git diff.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
