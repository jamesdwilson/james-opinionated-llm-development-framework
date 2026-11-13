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
- Scaffolding preserves existing project files. Reviewed gate application requires
  explicit preview confirmation. Never modify an existing Makefile.
  Anything unsafe to automate becomes a numbered instruction instead.

Usage:
  adopt.py plan TARGET_DIR --command TASK DIRECTORY COMMAND [--command ...]
  adopt.py plan TARGET_DIR --preview-gate --command TASK DIRECTORY COMMAND [...]
  adopt.py plan TARGET_DIR --apply-gate FINGERPRINT --command TASK DIRECTORY COMMAND [...]
  adopt.py audit  TARGET_DIR          read-only status report
  adopt.py install TARGET_DIR [--ci]  install missing safe pieces + GATE.md
"""

import ast
import contextlib
import difflib
import hashlib
import io
import json
import os
import platform
import shlex
import shutil
import subprocess
import sys
import stat
import tokenize
from datetime import datetime, timezone

ORDER = ["install", "test-e2e-install", "verify", "test", "build", "test-e2e"]

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


# --------------------------------------------------------------------------
# Adapter registry. To support another toolchain, add one entry here. Each
# adapter provides:
#   name        short identifier
#   detect(t, probe_versions=True) -> file facts and optional local version
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


def detect_go(t, probe_versions=True):
    if not os.path.isfile(os.path.join(t, "go.mod")):
        return None
    ver = _tool_version(["go", "version"]).split(" ")[2] if probe_versions and shutil.which("go") else ""
    return {"marker": "go.mod", "version": ver}


def detect_bun(t, probe_versions=True):
    # A generic JavaScript manifest supplies no Bun ownership evidence. Keep
    # conflicting or unreadable metadata on the explicit native-plan path.
    if not os.path.isfile(os.path.join(t, "bun.lock")):
        return None
    if any(os.path.lexists(os.path.join(t, name)) for name in
           ("package-lock.json", "npm-shrinkwrap.json", "pnpm-lock.yaml", "yarn.lock")):
        return None
    manifest = os.path.join(t, "package.json")
    if os.path.lexists(manifest):
        try:
            with open(manifest, encoding="utf-8") as fh:
                package = json.load(fh)
        except (OSError, UnicodeError, ValueError):
            return None
        if not isinstance(package, dict):
            return None
        if "packageManager" in package:
            declaration = package["packageManager"]
            if not isinstance(declaration, str) or not declaration.startswith("bun@") or not declaration[4:].strip():
                return None
    # These remain marker facts, without lockfile or declaration validation.
    facts = {"marker": "bun.lock", "lockfile": True}
    facts["version"] = _tool_version(["bun", "--version"]) if probe_versions and shutil.which("bun") else ""
    return facts


def detect_python(t, probe_versions=True):
    for marker in ("pyproject.toml", "requirements.txt", "setup.py", "Pipfile"):
        if os.path.isfile(os.path.join(t, marker)):
            ver = ""
            if probe_versions and shutil.which("python3"):
                ver = _tool_version(["python3", "--version"]).replace("Python ", "")
            return {"marker": marker, "version": ver,
                    "requirements": os.path.isfile(os.path.join(t, "requirements.txt"))}
    return None


def detect_rust(t, probe_versions=True):
    if not os.path.isfile(os.path.join(t, "Cargo.toml")):
        return None
    facts = {"marker": "Cargo.toml", "lockfile": os.path.isfile(os.path.join(t, "Cargo.lock"))}
    if probe_versions and shutil.which("cargo"):
        facts["version"] = _tool_version(["cargo", "--version"]).split(" ")[1]
    return facts


def detect_vite(t, strict_package_text=True):
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
        except UnicodeError:
            if strict_package_text:
                raise
            # Audit reports the manifest error separately; retain its Vite path.
            pkg_text = ""
        isolated = False
        for c in cfgs:
            if os.path.isfile(os.path.join(t, d, c)):
                with open(os.path.join(t, d, c)) as fh:
                    isolated = "envDir: false" in fh.read()
                if isolated:
                    break
        return {"dir": d if d != "." else "", "vitest": '"vitest"' in pkg_text,
                "configs": [os.path.normpath(os.path.join(d, c)) for c in sorted(cfgs)],
                "env_isolated": isolated,
                "typescript": os.path.isfile(os.path.join(t, d, "tsconfig.json"))}
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


def detect_all(target, probe_versions=True):
    found = {}
    for a in ADAPTERS:
        facts = a["detect"](target, probe_versions=probe_versions)
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


def report_package_scripts(target, vite):
    """Read declarations only, in root and the existing detector's single Vite match."""
    lines = ["  package scripts: unexecuted declarations/candidates; not verified native commands",
             "    scope: root plus recognised Vite frontend only; no general monorepo discovery",
             "    package manager: unresolved; package.json alone does not establish Bun"]
    directories = ["."]
    if vite and vite["dir"]:
        directories.append(vite["dir"])
    unresolved = 0
    for directory in directories:
        manifest = os.path.normpath(os.path.join(directory, "package.json"))
        source = "source manifest=%s; working directory=%s" % (json.dumps(manifest), json.dumps(directory))
        # Only an unobserved root manifest is optional. A detected Vite manifest
        # or a present path that disappears before reading remains unresolved.
        expected = directory != "." or bool(vite and not vite["dir"]) or os.path.lexists(os.path.join(target, manifest))

        def problem(reason):
            lines.append("    %s; unresolved discovery: %s" % (source, reason))

        try:
            with open(os.path.join(target, manifest), encoding="utf-8") as fh:
                package = json.load(fh)
        except FileNotFoundError:
            if expected:
                problem("manifest missing")
                unresolved += 1
            else:
                lines.append("    %s; manifest absent; root package scripts not applicable" % source)
            continue
        except (OSError, UnicodeError, ValueError) as exc:
            # Do not interpolate parser/file error text containing untrusted input.
            problem("invalid JSON" if isinstance(exc, (UnicodeError, ValueError)) else "manifest unreadable")
            unresolved += 1
            continue
        if not isinstance(package, dict):
            problem("manifest must be an object")
            unresolved += 1
            continue
        if "packageManager" not in package:
            lines.append("    manifest=%s; working directory=%s; packageManager absent; optional/informational" %
                         (json.dumps(manifest), json.dumps(directory)))
        elif not isinstance(package["packageManager"], str) or not package["packageManager"].strip():
            reason = "blank string" if isinstance(package["packageManager"], str) else "value must be a nonblank string"
            lines.append("    %s; packageManager unusable optional declaration: %s" % (source, reason))
        else:
            lines.append("    %s; packageManager=%s; declared/unverified; not format/pin/hash checked, installed, active or trusted; not an instruction" %
                         (source, json.dumps(package["packageManager"])))
            lines.append("    legacy root adapters/scaffold defaults are not chosen from this declaration; inspect native workflow and supply an explicit plan")
        # Reuse this parsed manifest; optional technical evidence adds no gaps.
        react_source = "React declaration: manifest=%s; working directory=%s" % (
            json.dumps(manifest), json.dumps(directory))
        lines.append("    React evidence limits: version/installation/support/actual framework execution unverified; "
                     "app vs library and DOM UI vs other target unknown; license/integrity unverified; "
                     "no tool or browser classification selected")
        declared = False
        sections_known = True
        for section in ("dependencies", "devDependencies", "peerDependencies", "optionalDependencies"):
            if section not in package:
                continue
            dependencies = package[section]
            section_source = "%s; dependency section=%s" % (react_source, json.dumps(section))
            if not isinstance(dependencies, dict):
                sections_known = False
                lines.append("    %s; unknown: optional section must be an object" % section_source)
                continue
            for name in ("react", "react-dom"):
                if name not in dependencies:
                    continue
                declared = True
                declaration = "%s; package=%s" % (section_source, json.dumps(name))
                value = dependencies[name]
                if not isinstance(value, str):
                    lines.append("    %s; unknown: declaration value must be a string" % declaration)
                else:
                    lines.append("    %s; value=%s; declaration only; not an instruction" %
                                 (declaration, json.dumps(value)))
        if not declared and sections_known:
            lines.append("    %s; no literal react/react-dom declarations; optional/informational" % react_source)
        scripts = package.get("scripts", {})
        if not isinstance(scripts, dict):
            problem("scripts must be an object")
            unresolved += 1
            continue
        if not scripts:
            lines.append("    %s; no scripts declared" % source)
        for name, command in scripts.items():
            if not isinstance(command, str):
                problem("script name=%s; script value must be a string" % json.dumps(name))
                unresolved += 1
                continue
            lines.append("    source manifest=%s; script name=%s; literal command=%s; working directory=%s" %
                         tuple(json.dumps(value) for value in (manifest, name, command, directory)))
    return lines, unresolved


def report_child_go_markers(target):
    """Bounded metadata evidence only; never add child facts to root adapters."""
    skip = {"node_modules", "vendor", "dist", "build", "target", "__pycache__", "venv"}
    lines = ["  child Go markers: unverified file presence; not parsed modules or verified commands",
             "    scope: immediate nonsymlink children only; root adapters remain root-only",
             "    deeper layouts uninspected; linked/nonregular markers uninspected",
             "    hidden and dependency/build directories uninspected (project policy): " + ", ".join(sorted(skip)),
             "    no runner, entrypoint, version or readiness selected; existing gaps unchanged"]
    try:
        flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_NONBLOCK
    except AttributeError:
        lines.append("    unknown/uninspected: required no-follow directory inspection unavailable")
        return lines
    candidates, unknown = 0, False

    def identity(metadata):
        return metadata.st_dev, metadata.st_ino, metadata.st_mode

    try:
        # Anchor metadata operations to open directories. Never follow a child or
        # marker link, including a directory replaced after enumeration.
        with contextlib.ExitStack() as stack:
            root_fd = os.open(target, flags)
            stack.callback(os.close, root_fd)
            with os.scandir(root_fd) as entries:
                children = sorted(entries, key=lambda entry: entry.name)
            for entry in children:
                if entry.name.startswith(".") or entry.name in skip:
                    continue
                source = "working directory=%s" % json.dumps(entry.name)
                try:
                    metadata = entry.stat(follow_symlinks=False)
                    if stat.S_ISLNK(metadata.st_mode):
                        lines.append("    %s; uninspected: linked directory entry" % source)
                        continue
                    if not stat.S_ISDIR(metadata.st_mode):
                        continue
                    with contextlib.ExitStack() as child_stack:
                        child_fd = os.open(entry.name, flags, dir_fd=root_fd)
                        child_stack.callback(os.close, child_fd)
                        if identity(metadata) != identity(os.fstat(child_fd)):
                            raise OSError("child changed")
                        source += "; marker path=%s" % json.dumps(entry.name + "/go.mod")
                        try:
                            marker = os.stat("go.mod", dir_fd=child_fd, follow_symlinks=False)
                        except FileNotFoundError:
                            marker = None
                        # Check that the owning directory still has the observed
                        # identity. Absence is only a scoped metadata observation.
                        if identity(metadata) != identity(os.stat(entry.name, dir_fd=root_fd, follow_symlinks=False)):
                            raise OSError("child changed")
                        if marker is None:
                            lines.append("    %s; marker absent at inspected location" % source)
                        elif not stat.S_ISREG(marker.st_mode):
                            lines.append("    %s; uninspected: linked or nonregular marker" % source)
                        else:
                            current = os.stat("go.mod", dir_fd=child_fd, follow_symlinks=False)
                            if identity(marker) != identity(current):
                                raise OSError("marker changed")
                            lines.append("    %s; unverified file presence" % source)
                            candidates += 1
                except (OSError, NotImplementedError):
                    unknown = True
                    lines.append("    %s; unknown/uninspected: metadata unavailable or changed" % source)
    except (OSError, NotImplementedError):
        unknown = True
        lines.append("    unknown/uninspected: cannot enumerate target")
    if not candidates and not unknown:
        lines.append("    no immediate-child candidates observed within this scope; not a claim of no Go anywhere")
    return lines


def report(target, found, missing, has_gate_py, vite, pw, dev, osname, probe_versions=True):
    lines = [
        "quality gate report: %s" % target,
        "  operating system:          %s" % osname,
        "  adapters matched:          %s" % (", ".join(sorted(found)) or "none"),
        "  marker evidence:",
    ]
    for name in sorted(found):
        facts = found[name][1]
        if not probe_versions:
            facts = dict(facts, version="unprobed")
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

ORDER = {order}


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
        if vite.get("typescript", False):
            commands["test"] += ["bun --no-env-file run --bun --cwd %s tsc --noEmit" % d]
            commands["build"] += ["bun --no-env-file run --bun --cwd %s tsc -b" % d]
        commands["test"] += ["bun --no-env-file run --bun --cwd %s test" % d]
        commands["build"] += ["bun --no-env-file run --bun --cwd %s vite build" % d]
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
        order=json.dumps(ORDER), env=fmt(env, 1), lockfiles=fmt(lockfiles, 0), pins=fmt(pins, 0),
        build_dirs=fmt(build_dirs, 0), commands=fmt(commands, 1))


def read_reviewed_gate(path):
    """Read a regular nonsymlink gate and capture ordinary conflict identity."""
    if not stat.S_ISREG(os.lstat(path).st_mode):
        raise ValueError("gate.py must be a regular nonsymlink file")
    flags = os.O_RDONLY | os.O_NONBLOCK | os.O_NOFOLLOW
    with os.fdopen(os.open(path, flags), "rb") as stream:
        metadata = os.fstat(stream.fileno())
        if not stat.S_ISREG(metadata.st_mode):
            raise ValueError("gate.py must be a regular nonsymlink file")
        content = stream.read()
    identity = (metadata.st_dev, metadata.st_ino, metadata.st_mode,
                metadata.st_size, metadata.st_mtime_ns, metadata.st_ctime_ns)
    return content, identity


def reviewed_gate_bytes(original, commands):
    """Insert only missing commands using AST byte positions, retaining source bytes."""
    encoding, _ = tokenize.detect_encoding(io.BytesIO(original).readline)
    if encoding not in ("utf-8", "utf-8-sig"):
        raise ValueError("reviewed gate requires UTF-8 source")
    text = original.decode(encoding)
    tree = ast.parse(text)
    assignments = [node for node in tree.body if isinstance(node, ast.Assign)
                   and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name)
                   and node.targets[0].id == "COMMANDS"]
    if len(assignments) != 1:
        raise ValueError("exactly one simple module-level COMMANDS assignment required")
    assignment = assignments[0]
    parents = {child: node for node in ast.walk(tree) for child in ast.iter_child_nodes(node)}
    # Only ordinary task iteration reads are admitted. Aliases and indirect
    # mutation are outside this bounded editor's supported gate shape.
    # These declarations store bound identifiers outside ast.Name. Inspect all
    # scopes, just as for Name targets below; this is a shape check, not scope
    # resolution or a guarantee about arbitrary Python behaviour.
    named_bindings = (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.ExceptHandler) + tuple(
        getattr(ast, name) for name in ("MatchAs", "MatchStar", "TypeVar", "ParamSpec", "TypeVarTuple")
        if hasattr(ast, name))
    match_mapping = getattr(ast, "MatchMapping", ())
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            # `import a.b` binds a; `import a.b as c` binds c.
            names = [alias.asname or alias.name.split(".")[0] for alias in node.names]
        elif isinstance(node, ast.ImportFrom):
            names = [alias.asname or alias.name for alias in node.names]
            if any(alias.name == "*" for alias in node.names):
                raise ValueError("unsupported COMMANDS binding: wildcard import")
        elif isinstance(node, named_bindings):
            names = [node.name]
        elif isinstance(node, ast.arg):
            names = [node.arg]
        elif isinstance(node, match_mapping):
            names = [node.rest]
        elif isinstance(node, (ast.Global, ast.Nonlocal)):
            if "COMMANDS" in node.names:
                raise ValueError("unsupported COMMANDS scope declaration")
            names = []
        else:
            names = []
        if "COMMANDS" in names:
            raise ValueError("unsupported COMMANDS binding")
        if not isinstance(node, ast.Name) or node.id != "COMMANDS" or node is assignment.targets[0]:
            continue
        parent = parents[node]
        read = parent
        if isinstance(parent, ast.Attribute) and parent.attr == "get":
            read = parents.get(parent)
            if not isinstance(read, ast.Call) or read.func is not parent:
                raise ValueError("unsupported COMMANDS reference or mutation")
        elif not isinstance(parent, ast.Subscript) or not isinstance(parent.ctx, ast.Load):
            raise ValueError("unsupported COMMANDS reference or mutation")
        owner = parents.get(read)
        if not isinstance(owner, ast.For) or owner.iter is not read or not isinstance(node.ctx, ast.Load):
            raise ValueError("unsupported COMMANDS reference or mutation")
    value = assignment.value
    if not isinstance(value, ast.Dict):
        raise ValueError("COMMANDS must be a literal dictionary")
    lists = {}
    for key, items in zip(value.keys, value.values):
        if not isinstance(key, ast.Constant) or not isinstance(key.value, str) or key.value not in ORDER:
            raise ValueError("COMMANDS keys must be known task strings")
        if key.value in lists:
            raise ValueError("duplicate COMMANDS task: " + ascii(key.value))
        if not isinstance(items, ast.List) or any(not isinstance(item, ast.Constant)
                                                or not isinstance(item.value, str) for item in items.elts):
            raise ValueError("COMMANDS values must be literal lists of strings")
        lists[key.value] = items
    # AST columns count UTF-8 bytes. A BOM is outside those columns.
    lines = text.encode("utf-8").splitlines(keepends=True)
    offsets = [len(original) - len(text.encode("utf-8"))]
    for line in lines:
        offsets.append(offsets[-1] + len(line))
    edits = []
    for task, selected in commands.items():
        if task not in lists:
            raise ValueError("selected task absent from COMMANDS: " + ascii(task))
        items = lists[task]
        present = [item.value for item in items.elts]
        missing = []
        for command in selected:
            if command not in present:
                missing.append(command)
                present.append(command)
        if not missing:
            continue
        # Tokenization distinguishes an existing trailing comma from comments
        # and parenthesized literals without interpreting Python text ourselves.
        segment = ast.get_source_segment(text, items)
        tokens = [token for token in tokenize.generate_tokens(io.StringIO(segment).readline)
                  if token.type not in (tokenize.NL, tokenize.NEWLINE, tokenize.COMMENT,
                                        tokenize.ENDMARKER, tokenize.INDENT, tokenize.DEDENT)]
        trailing_comma = tokens[-2].string == ","
        prefix = ", " if items.elts and not trailing_comma else " "
        position = offsets[items.end_lineno - 1] + items.end_col_offset - 1
        insertion = prefix + ", ".join(ascii(command) for command in missing)
        edits.append((position, insertion.encode("ascii")))
    result = original
    for position, insertion in sorted(edits, reverse=True):
        result = result[:position] + insertion + result[position:]
    # Fail closed if the resulting source cannot be parsed.
    ast.parse(result)
    return result


def apply_reviewed_gate(path, original, identity, result):
    """Prepare bounded recovery files and atomically replace after a final check."""
    mode = stat.S_IMODE(identity[2])
    backup = (path + ".reviewed-backup-sha256-" + hashlib.sha256(original).hexdigest()
              + "-mode-" + format(mode, "04o"))
    temporary = path + ".reviewed-tmp"
    try:
        if os.path.lexists(temporary):
            raise ValueError("temporary recovery path already exists: " + ascii(temporary))
        prepared = []
        if os.path.lexists(backup):
            try:
                retained, metadata = read_reviewed_gate(backup)
            except (OSError, ValueError) as error:
                raise ValueError("retained backup regular/nonsymlink verification failed: "
                                 + ascii(backup)) from error
            if retained != original or stat.S_IMODE(metadata[2]) != mode:
                raise ValueError("retained backup content/mode mismatch: " + ascii(backup))
        else:
            prepared.append((backup, original))
        prepared.append((temporary, result))
        for destination, content in prepared:
            with os.fdopen(os.open(destination, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600), "wb") as stream:
                stream.write(content)
                stream.flush()
                os.fchmod(stream.fileno(), mode)
                os.fsync(stream.fileno())
        if read_reviewed_gate(path) != (original, identity):
            raise ValueError("gate.py changed during preparation; recovery files retained")
        os.replace(temporary, path)
    except (OSError, ValueError) as error:
        raise ValueError(str(error) + "; inspect target and recovery paths " + ascii(backup)
                         + " and " + ascii(temporary)
                         + "; preserve evidence, manually restore verified bytes/mode or relocate"
                         + " incomplete recovery files before a fresh preview/retry") from error
    return backup



def reviewed_gate(target, selections, commands, expected):
    path = os.path.join(target, "gate.py")
    original, identity = read_reviewed_gate(path)
    result = reviewed_gate_bytes(original, commands)
    binding = json.dumps([path, original.hex(), stat.S_IMODE(identity[2]), selections, result.hex()],
                         ensure_ascii=True, separators=(",", ":")).encode("ascii")
    fingerprint = hashlib.sha256(binding).hexdigest()
    if expected is not None:
        if expected != fingerprint:
            raise ValueError("confirmation mismatch; preview the unchanged target and selections first")
        if result != original:
            backup = apply_reviewed_gate(path, original, identity, result)
            print("Retained original backup: " + ascii(backup))
        print("Applied reviewed gate.py." if result != original else "No changes to gate.py.")
        print("Selected commands remain unexecuted; task execution requires separate authority.")
        return 0
    # JSON framing keeps terminal controls inert. Explicit missing-newline
    # markers make the unified diff describe those source bytes as well.
    diff_lines = difflib.diff_bytes(difflib.unified_diff,
                 original.splitlines(keepends=True), result.splitlines(keepends=True),
                 fromfile=b"a/gate.py", tofile=b"b/gate.py", lineterm=b"\n")
    diff = b"".join(line if line.endswith(b"\n") else line + b"\n\\ No newline at end of file\n"
                    for line in diff_lines)
    print("Human review diff (display-only; do not paste/apply):")
    print("LF gives layout; backslashes doubled; other controls/non-ASCII use \\uXXXX/\\UXXXXXXXX.")
    print("Exact JSON below is authoritative for byte copying after decoding.")
    display = "".join("\\\\" if char == "\\" else char if char == "\n" or " " <= char <= "~"
                      else ("\\u%04x" if ord(char) <= 0xffff else "\\U%08x") % ord(char)
                      for char in diff.decode("utf-8"))
    for line in display.removesuffix("\n").split("\n") if display else ["(no changes)"]:
        print("| " + line)
    print("Exact unified diff as a JSON-escaped UTF-8 string (decode to recover diff bytes):")
    print(json.dumps(diff.decode("utf-8"), ensure_ascii=True))
    print("Confirmation SHA256: " + fingerprint)
    return 0


def plan(argv):
    """Validate explicit selections completely before rendering an inert preview."""
    def invalid(message):
        sys.stderr.write("plan: " + message + "\n")
        return 2

    if len(argv) < 3 or argv[2] == "":
        return invalid("target required; use plan TARGET --command TASK DIRECTORY COMMAND")
    try:
        target = os.path.realpath(argv[2])
    except (OSError, ValueError):
        return invalid("target not found: " + ascii(argv[2]))
    if not os.path.isdir(target):
        return invalid("target not found: " + ascii(argv[2]))
    arguments = argv[3:]
    reviewed = False
    expected = None
    if arguments and arguments[0] == "--preview-gate":
        reviewed = True
        arguments = arguments[1:]
    elif arguments and arguments[0] == "--apply-gate":
        if len(arguments) < 2 or len(arguments[1]) != 64 or any(c not in "0123456789abcdef" for c in arguments[1]):
            return invalid("--apply-gate requires the expected preview SHA256 fingerprint")
        reviewed = True
        expected = arguments[1]
        arguments = arguments[2:]
    if not arguments:
        return invalid("at least one --command is required")
    selections = []
    commands = {}
    while arguments:
        if arguments[0] != "--command":
            return invalid("unknown option: " + ascii(arguments[0]))
        if len(arguments) < 4:
            return invalid("--command requires TASK DIRECTORY COMMAND")
        task, directory, command = arguments[1:4]
        arguments = arguments[4:]
        if task not in ORDER:
            return invalid("unknown task: " + ascii(task) + "; choose " + ", ".join(ORDER))
        if reviewed and "\x00" in command:
            return invalid("command contains NUL for " + ascii(task))
        if not command.strip():
            return invalid("command must be nonblank for " + ascii(task))
        if os.path.isabs(directory):
            return invalid("directory must be target-relative: " + ascii(directory))
        if ".." in directory.split(os.sep):
            return invalid("directory traversal is not allowed: " + ascii(directory))
        # Embedded NUL cannot name a filesystem directory.
        if not directory or "\x00" in directory:
            return invalid("directory not found: " + ascii(directory))
        try:
            resolved = os.path.realpath(os.path.join(target, directory))
        except (OSError, ValueError):
            return invalid("directory not found: " + ascii(directory))
        if os.path.commonpath([target, resolved]) != target:
            return invalid("directory resolves outside target: " + ascii(directory))
        if not os.path.isdir(resolved):
            return invalid("directory not found: " + ascii(directory))
        selections.append((task, directory, command))
        commands.setdefault(task, []).append("(cd " + shlex.quote(os.path.join(".", directory)) + " && (\n" + command + "\n))")

    # JSON escaping plus a table-delimiter escape keeps each value on one row.
    def cell(value):
        return json.dumps(value, ensure_ascii=True).replace("|", "\\u007c")

    lines = ["quality gate plan: " + json.dumps(target),
             "Scope: explicitly supplied/unverified commands; proposed, unexecuted.",
             "Provenance is supplied by the person or LLM after inspecting doctor output.",
             "Command declarations and runners require manual review.",
             "| Role/task | Existing tool or practice | Keep, add, N/A, blocked, or not run | Reason |",
             "|---|---|---|---|"]
    for task, directory, command in selections:
        lines.append("| %s | directory=%s; command=%s | proposed, unexecuted | explicitly supplied/unverified |" %
                     (task, cell(directory), cell(command)))
    lines += ["Remaining manual tasks: " + (", ".join(task for task in ORDER if task not in commands) or "none unselected"),
              "Remaining manual roles: Project Brief, BDD discovery, TDD and fast tests, Browser journeys, "
              "Bounded UX review, Error capture and recovery, Supply-chain checks, Candidate evidence and review.",
              "Review applicability, prerequisites, required checks and evidence for every role/task."]
    if reviewed:
        try:
            # Buffer output so refusals never publish a partial preview/confirmation.
            with io.StringIO() as output, contextlib.redirect_stdout(output):
                status = reviewed_gate(target, selections, commands, expected)
                rendered = output.getvalue()
            print("\n".join(lines))
            print(rendered, end="")
            return status
        except (OSError, ValueError, SyntaxError, UnicodeError, RecursionError) as error:
            return invalid(ascii(str(error)))
    lines += ["Paste-ready entries for the existing generated COMMANDS dict (run gate.py from the target root):",
              "Replace selected COMMANDS entries only after human/agent review preserving all existing required checks.",
              "Selected lists replace each selected task's whole list. Review and merge required checks before applying.",
              "Execution and auto-apply remain separately authorised/manual.",
              "```python"]
    for task, selected in commands.items():
        lines.append("    " + ascii(task) + ": [")
        lines.extend("        " + ascii(command) + "," for command in selected)
        lines.append("    ],")
    lines.append("```")
    print("\n".join(lines))
    return 0


def main(argv):
    if len(argv) > 1 and argv[1] == "plan":
        return plan(argv)
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
    found = detect_all(target, probe_versions=mode == "install")
    vite = detect_vite(target, strict_package_text=mode == "install")
    pw = detect_playwright(target)
    mf = find_makefile_gaps(target)
    has_gate_py = os.path.isfile(os.path.join(target, "gate.py"))
    dev = dev_safety(target)
    lines = report(target, found, mf, has_gate_py, (vite["dir"] or ".") if vite else None, pw, dev, osname,
                   probe_versions=mode == "install")

    if mode == "audit":
        script_lines, unresolved_scripts = report_package_scripts(target, vite)
        lines += script_lines
        lines += report_child_go_markers(target)
        if vite:
            lines.append("  Vite marker evidence: %s" % ", ".join(vite["configs"]))
        if pw:
            lines.append("  Playwright marker evidence: %s" % ", ".join(pw["configs"]))
        lines += ["  commands: unverified defaults; no commands executed",
                  "  readiness: unproven; marker matches do not verify native commands or safety"]
        print("\n".join(lines))
        gaps = (0 if has_gate_py else len(mf[1])) + unresolved_scripts
        gaps += 0 if (vite and vite["env_isolated"]) else (1 if vite else 0)
        gaps += 0 if dev == "present" else 1
        if gaps == 0:
            print("verdict: gate shape present. Run the acceptance gate (fresh checkout chain, "
                  "start/restart smoke, one bounded review) before claiming qualification.")
        else:
            print("verdict: %d gap group(s)." % gaps)
            print("Review remaining applicability, declarations and safety in the adoption map; "
                  "scaffolding does not resolve all reported gaps. Do not infer service requirements.")
            if has_gate_py:
                print("Preserve existing gate.py; source shape is unverified by doctor. "
                      "Review explicit selections with plan, then --preview-gate for a supported literal gate; "
                      "confirm its diff with --apply-gate FINGERPRINT and identical selections. "
                      "Unsupported source needs manual adaptation; preserve every required check.")
            elif mf[0] is not None:
                print("Preserve existing Makefile; review explicit selections and transfer into native recipes. "
                      "Add missing targets manually where applicable; target-name matches do not verify recipes.")
            elif found:
                print("Optional scaffolding for the missing gate requires Git and explicit write authority. "
                      "Review generated defaults; existing GATE.md entries are preserved.")
                print("Scaffolding command (JSON string; decode before use): " +
                      json.dumps(shlex.join(["python3", "quality-gate/install", target]), ensure_ascii=True))
            else:
                print("No adapter matched; use a manual native gate owner and review explicit selections. "
                      "Scaffold installation would refuse this target.")
            print("Plan command (JSON string; decode before use): " +
                  json.dumps(shlex.join(["python3", "quality-gate/adopt.py", "plan", target,
                                         "--command", "TASK", "DIRECTORY", "COMMAND"]), ensure_ascii=True))
            print("Replace TASK DIRECTORY COMMAND with inspected native selections; see WALKTHROUGH.md. "
                  "Native check execution requires separate authority; no command was executed.")
        return 0

    # install mode
    if subprocess.run(["git", "-C", target, "rev-parse", "--is-inside-work-tree"],
                      capture_output=True).returncode != 0:
        sys.stderr.write("refusing: target is not a git repository (review needs a diff boundary)\n")
        return 1
    if not found:
        sys.stderr.write("refusing: no adapter matched; nothing to wire. "
                         "Inspect native tooling and use an explicit plan with a manual native gate owner.\n")
        return 1

    # Bun-specific defaults belong only to the directory supplying Bun evidence.
    # Other components retain their inspected native owner through explicit plans.
    bun_vite = vite if vite and detect_bun(os.path.join(target, vite["dir"]), probe_versions=False) else None
    bun_pw = None
    if pw:
        pw_directory = os.path.join(target, os.path.dirname(pw["configs"][0]))
        # Inherit only from the closest directory with manager metadata. Never
        # jump past a native or unresolved frontend owner to the root toolchain.
        manager_markers = ("package.json", "bun.lock", "package-lock.json", "npm-shrinkwrap.json", "pnpm-lock.yaml", "yarn.lock")
        while pw_directory != target and not any(
                os.path.lexists(os.path.join(pw_directory, name)) for name in manager_markers):
            pw_directory = os.path.dirname(pw_directory)
        if detect_bun(pw_directory, probe_versions=False):
            bun_pw = pw
    installed = []
    if has_gate_py or mf[0] is not None:
        missing_targets = [] if has_gate_py else mf[1]
    else:
        with open(os.path.join(target, "gate.py"), "w") as fh:
            fh.write(emit_gate_py(found, bun_pw, bun_vite))
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

    if bun_vite and vite["vitest"]:
        dest = os.path.join(target, vite["dir"] or ".", "env-isolation.test.ts")
        if not os.path.isfile(dest):
            shutil.copyfile(os.path.join(SCRIPT_DIR, "templates", "env-isolation.test.ts"), dest)
            installed.append(os.path.relpath(dest, target) + "(template)")

    steps = []
    if (vite and not bun_vite) or (pw and not bun_pw):
        steps.append("Detected JavaScript configuration requires an explicit native plan. "
                     "Inspect its owning directory, manager policy and documented commands; "
                     "review and apply selections through the existing native gate owner. "
                     "Bun-specific commands and isolation templates require unconflicted Bun markers.")
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
    if bun_vite and not vite["env_isolated"]:
        steps.append("Set `envDir: false` in every Vite config in `%s`, run Bun-owned test workers "
                     "with `--no-env-file` (worker execArgv, not just the parent), and keep the "
                     "planted env-isolation regression green." % (vite["dir"] or "."))
    if bun_vite and vite["vitest"]:
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
        "Generated by quality-gate/adopt.py on %s. Review and adapt these steps; existing GATE.md is preserved on rerun."
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
    guide_written = False
    try:
        with open(os.path.join(target, "GATE.md"), "x", encoding="utf-8") as fh:
            fh.write("\n".join(gate_doc))
        guide_written = True
    except FileExistsError:
        pass

    print("\n".join(lines))
    print("\ninstalled: %s" % (" ".join(installed) if installed else "nothing"))
    if guide_written:
        print("wrote GATE.md with the remaining steps. Review everything as a normal git diff.")
    else:
        print("preserved existing GATE.md entry; inspect it and reconcile remaining steps manually. "
              "Review everything as a normal git diff.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
