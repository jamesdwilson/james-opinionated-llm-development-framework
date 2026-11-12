"""Bounded regressions for generated command dispatch and Python installation.
Run: python3 -m unittest discover -s quality-gate -p 'test_*.py' -v
"""
import ast
import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import runpy
import shlex
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

SPEC = importlib.util.spec_from_file_location("adopt", Path(__file__).with_name("adopt.py"))
assert SPEC is not None and SPEC.loader is not None
adopt = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(adopt)


class AdoptionContracts(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(prefix="gate-regression-")
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)

    def plan(self, *args, target=None):
        output, errors = io.StringIO(), io.StringIO()
        before = self.snapshot(self.root)
        with mock.patch.object(adopt.subprocess, "run", side_effect=AssertionError("subprocess forbidden")) as run, \
             mock.patch.object(adopt.os, "system", side_effect=AssertionError("shell forbidden")), \
             mock.patch("builtins.open", side_effect=AssertionError("planning must not read target files")), \
             contextlib.redirect_stdout(output), contextlib.redirect_stderr(errors):
            code = adopt.main(["adopt.py", "plan", str(self.root if target is None else target), *args])
        run.assert_not_called()
        self.assertEqual(before, self.snapshot(self.root))
        return code, output.getvalue(), errors.getvalue()

    def entries(self, output):
        return ast.literal_eval("{" + output.split("```python\n", 1)[1].split("```", 1)[0] + "}")

    def test_plan_mixed_order_custom_and_deterministic(self):
        for name in ("backend", "frontend", "services/api"):
            (self.root / name).mkdir(parents=True)
        args = ("--command", "test", "backend", "go test ./...",
                "--command", "build", "frontend", "npm run bundle:ui",
                "--command", "test", "frontend", "npm run ui:check",
                "--command", "test", "services/api", "custom-check")
        code, output, errors = self.plan(*args)
        self.assertEqual((code, errors), (0, ""))
        self.assertEqual(self.plan(*args), (code, output, errors))
        entries = self.entries(output)
        self.assertEqual(list(entries), ["test", "build"])
        self.assertEqual(entries["test"], ["(cd ./backend && (\ngo test ./...\n))",
                         "(cd ./frontend && (\nnpm run ui:check\n))",
                         "(cd ./services/api && (\ncustom-check\n))"])
        self.assertLess(output.index("go test"), output.index("bundle:ui"))
        self.assertIn("explicitly supplied/unverified", output)
        self.assertIn("proposed, unexecuted", output)

    def test_plan_partial_poison_files_and_no_execution(self):
        for name in ("gate.py", "vite.config.py", "package.json", "Makefile"):
            (self.root / name).write_text("raise AssertionError('never execute or parse')")
        code, output, errors = self.plan("--command", "test", ".", "false; echo NEVER_EXECUTE")
        self.assertEqual((code, errors), (0, ""))
        self.assertEqual(list(self.entries(output)), ["test"])
        for task in ("install", "test-e2e-install", "verify", "build", "test-e2e"):
            self.assertIn(task, output.split("Remaining manual tasks", 1)[1])
        self.assertIn("Project Brief", output)
        self.assertIn("preserving all existing required checks", output)

    def test_plan_invalid_selections_have_no_snippet(self):
        (self.root / "inside").mkdir()
        (self.root / "outside-link").symlink_to(self.root.parent, target_is_directory=True)
        cases = [([], "at least one --command"),
                 (["--command", "bogus\nREADY", ".", "true"], "unknown task"),
                 (["--command", "test", "."], "requires TASK DIRECTORY COMMAND"),
                 (["--script", "test", ".", "check", "npm run check"], "unknown option"),
                 (["--command", "test", ".", " \t"], "command must be nonblank"),
                 (["--command", "test", "missing", "true"], "directory not found"),
                 (["--command", "test", str(self.root), "true"], "target-relative"),
                 (["--command", "test", "inside/../inside", "true"], "traversal"),
                 (["--command", "test", "outside-link", "true"], "outside target")]
        for args, diagnostic in cases:
            with self.subTest(args=args):
                code, output, errors = self.plan("--command", "build", ".", "true", *args) if args else self.plan()
                self.assertEqual(code, 2)
                self.assertIn(diagnostic, errors)
                self.assertNotIn("```python", output)
                self.assertNotIn("\nREADY", errors)
        code, output, errors = self.plan("--command", "test", ".", "true", target=self.root / "absent")
        self.assertEqual(code, 2)
        self.assertIn("target not found", errors)
        self.assertEqual(output, "")
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(adopt.main(["adopt.py", "plan"]), 2)

    def test_plan_empty_target_rejected_and_explicit_current_directory_allowed(self):
        before = self.snapshot(self.root)
        with self.subTest(entrypoint="owner-layer"):
            code, output, errors = self.plan("--command", "test", ".", "true", target="")
            self.assertEqual(code, 2)
            self.assertIn("target required", errors)
            self.assertEqual(output, "")
        entrypoint = str(Path(__file__).with_name("adopt.py"))
        for target, expected_code in (("", 2), (".", 0)):
            with self.subTest(target=target):
                result = subprocess.run(
                    [sys.executable, entrypoint, "plan", target, "--command", "test", ".", "true"],
                    cwd=self.root, capture_output=True, text=True, timeout=15)
                self.assertEqual(result.returncode, expected_code, result.stdout + result.stderr)
                if target == "":
                    self.assertEqual(result.stdout, "")
                    self.assertIn("target required", result.stderr)
                else:
                    self.assertIn("```python", result.stdout)
                    self.assertIn(str(self.root.resolve()), result.stdout)
                    self.assertEqual(result.stderr, "")
        self.assertEqual(before, self.snapshot(self.root))

    def test_plan_all_tasks_inside_symlink_and_public_entrypoint(self):
        (self.root / "-internal").mkdir()
        (self.root / "inside-link").symlink_to(self.root / "-internal", target_is_directory=True)
        tasks = ["install", "test-e2e-install", "verify", "test", "build", "test-e2e"]
        args = [value for task in tasks for value in ("--command", task, "inside-link", "true")]
        code, expected, errors = self.plan(*args)
        self.assertEqual((code, errors), (0, ""))
        self.assertEqual(list(self.entries(expected)), tasks)
        before = self.snapshot(self.root)
        output = io.StringIO()
        with mock.patch.object(sys, "argv", [str(Path(adopt.__file__)), "plan", str(self.root), *args]), \
             mock.patch.object(subprocess, "Popen", side_effect=AssertionError("subprocess forbidden")) as popen, \
             mock.patch.object(os, "system", side_effect=AssertionError("shell forbidden")), \
             contextlib.redirect_stdout(output), self.assertRaises(SystemExit) as exit_result:
            runpy.run_path(str(Path(adopt.__file__)), run_name="__main__")
        self.assertEqual(exit_result.exception.code, 0)
        popen.assert_not_called()
        self.assertEqual(output.getvalue(), expected)
        self.assertEqual(before, self.snapshot(self.root))

    def test_plan_control_characters_and_python_round_trip(self):
        directory = "a 'space|\nreadiness: verified\x1b"
        (self.root / directory).mkdir()
        command = "printf '%s' 'a|b'\n# readiness: verified\r\t\x1b\x00"
        code, output, errors = self.plan("--command", "test", directory, command)
        self.assertEqual((code, errors), (0, ""))
        self.assertEqual(self.entries(output)["test"], ["(cd " + shlex.quote(os.path.join(".", directory)) + " && (\n" + command + "\n))"])
        self.assertNotIn("\nreadiness: verified", output)
        for character in ("\r", "\t", "\x1b", "\x00"):
            self.assertNotIn(character, output)
        self.assertEqual(sum(line.startswith("| test |") for line in output.splitlines()), 1)

    def test_plan_manual_apply_ordinary_gate_order_and_fail_first(self):
        directory = "-back end's"
        (self.root / directory).mkdir()
        (self.root / "frontend").mkdir()
        record = self.root / "order.txt"
        command = "pwd >> " + shlex.quote(str(record))
        code, output, errors = self.plan("--command", "test", directory, command,
                                         "--command", "test", "frontend", command)
        self.assertEqual((code, errors), (0, ""))
        path = self.root / "gate.py"
        generated = adopt.emit_gate_py({}, None, None)
        tree = ast.parse(generated)
        assignment = next(node for node in tree.body if isinstance(node, ast.Assign)
                          and any(isinstance(t, ast.Name) and t.id == "COMMANDS" for t in node.targets))
        original = ast.literal_eval(assignment.value)
        lines = generated.splitlines(keepends=True)

        def apply_snippet(preview):
            selected = self.entries(preview)
            untouched = "".join("    " + repr(task) + ": " + repr(commands) + ",\n"
                                for task, commands in original.items() if task not in selected)
            snippet = preview.split("```python\n", 1)[1].split("```", 1)[0]
            path.write_text("".join(lines[:assignment.lineno-1]) + "COMMANDS = {\n" +
                            untouched + snippet + "}\n" + "".join(lines[assignment.end_lineno:]))

        apply_snippet(output)
        result = self.run_gate(path, "test")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(record.read_text().splitlines(), [str(self.root / directory), str(self.root / "frontend")])
        record.unlink()
        code, output, errors = self.plan("--command", "test", directory, "exit 7",
                                         "--command", "test", "frontend", command)
        apply_snippet(output)
        result = self.run_gate(path, "test")
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(record.exists())
        # A failed directory change gates every segment of a selected command.
        code, output, errors = self.plan("--command", "test", "frontend", "true; " + command)
        (self.root / "frontend").rmdir()
        apply_snippet(output)
        result = self.run_gate(path, "test")
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(record.exists())

    def generated(self, marker="pyproject.toml", requirements=False):
        (self.root / marker).write_text("" if marker != "pyproject.toml" else "[project]\nname='fixture'\nversion='0.0.0'\n")
        if requirements:
            (self.root / "requirements.txt").write_text("")
        facts = adopt.detect_python(str(self.root))
        adapter = next(a for a in adopt.ADAPTERS if a["name"] == "python")
        path = self.root / "gate.py"
        path.write_text(adopt.emit_gate_py({"python": (adapter, facts)}, None, None))
        return path

    def run_gate(self, path, *args):
        return subprocess.run([sys.executable, str(path), *args], cwd=self.root,
                              capture_output=True, text=True, timeout=15)

    def snapshot(self, root):
        return {p.relative_to(root): p.read_bytes() for p in root.rglob("*") if p.is_file()}

    def audit_scripts(self):
        before = self.snapshot(self.root)
        output = io.StringIO()
        with mock.patch.object(adopt.subprocess, "run", side_effect=AssertionError("subprocess forbidden")) as run, \
             contextlib.redirect_stdout(output):
            self.assertEqual(adopt.main(["adopt.py", "audit", str(self.root)]), 0)
        run.assert_not_called()
        self.assertEqual(before, self.snapshot(self.root))
        text = output.getvalue()
        self.assertIn("unexecuted declarations/candidates", text)
        self.assertIn("readiness: unproven", text)
        self.assertIn("package manager: unresolved", text)
        return text

    def test_script_mixed_go_root_and_nested_react_vite(self):
        (self.root / "go.mod").write_text("module example.invalid/synthetic\n")
        (self.root / "package.json").write_text(json.dumps({"scripts": {"api:check": "go test ./..."}}))
        web = self.root / "frontend"
        web.mkdir()
        (web / "package.json").write_text(json.dumps({"dependencies": {"react": "synthetic"},
                                                     "scripts": {"ui:check": "vitest run", "bundle:ui": "vite build"}}))
        (web / "vite.config.js").write_text("throw new Error('never execute config');")
        other = self.root / "unrecognised"
        other.mkdir()
        (other / "package.json").write_text('{"scripts":{"outside-scope":"DO_NOT_REPORT"}}')
        text = self.audit_scripts()
        for manifest, name, command, directory in (("package.json", "api:check", "go test ./...", "."),
                ("frontend/package.json", "ui:check", "vitest run", "frontend"),
                ("frontend/package.json", "bundle:ui", "vite build", "frontend")):
            self.assertIn('source manifest=%s; script name=%s; literal command=%s; working directory=%s' %
                          tuple(json.dumps(v) for v in (manifest, name, command, directory)), text)
        self.assertNotIn("DO_NOT_REPORT", text)
        self.assertIn("scope: root plus recognised Vite frontend only", text)
        self.assertIn("package.json alone does not establish Bun", text)

    def test_script_root_vite_deduplicated(self):
        (self.root / "package.json").write_text('{"scripts":{"custom":"echo candidate"}}')
        (self.root / "vite.config.js").write_text("throw new Error('never execute');")
        text = self.audit_scripts()
        self.assertEqual(text.count('script name="custom"'), 1)
        self.assertEqual(text.count('source manifest="package.json"'), 1)
        self.assertIn('working directory="."', text)

    def test_script_absent_and_empty_are_not_malformed(self):
        for manifest in ({}, {"scripts": {}}):
            with self.subTest(manifest=manifest):
                (self.root / "package.json").write_text(json.dumps(manifest))
                text = self.audit_scripts()
                self.assertIn("no scripts declared", text)
                self.assertNotIn("unresolved discovery:", text)

    def check_root_manifest_absence_compatibility(self, files):
        for name, content in {"gate.py": "raise AssertionError('never import')",
                              "Makefile": "dev:\n\tfalse # never execute\n", **files}.items():
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)
        text = self.audit_scripts()
        self.assertIn('source manifest="package.json"; working directory="."; manifest absent; root package scripts not applicable', text)
        self.assertNotIn("unresolved discovery:", text)
        self.assertIn("verdict: gate shape present", text)
        self.assertNotIn("Run: quality-gate/install", text)
        return text

    def test_script_root_absence_compatibility_pure_go(self):
        self.check_root_manifest_absence_compatibility({"go.mod": "module example.invalid/synthetic\n"})

    def test_script_root_absence_compatibility_pure_python(self):
        self.check_root_manifest_absence_compatibility({"pyproject.toml": "[project]\nname='synthetic'\n"})

    def test_script_root_absence_compatibility_neutral(self):
        self.check_root_manifest_absence_compatibility({"README.md": "Synthetic no-JavaScript fixture\n"})

    def test_script_root_absence_compatibility_nested_only_frontend(self):
        text = self.check_root_manifest_absence_compatibility({
            "frontend/package.json": '{"scripts":{"ui:check":"vitest run"}}',
            "frontend/vite.config.js": "// envDir: false\nthrow new Error('never execute');"})
        self.assertIn('source manifest="frontend/package.json"; script name="ui:check"; literal command="vitest run"; working directory="frontend"', text)

    def test_script_malformed_and_wrong_types_are_unresolved(self):
        for content, reason in (("{", "invalid JSON"),
                ("[]", "manifest must be an object"), ("null", "manifest must be an object"),
                ('{"scripts":[]}', "scripts must be an object"),
                ('{"scripts":null}', "scripts must be an object"),
                ('{"scripts":"test"}', "scripts must be an object")):
            with self.subTest(content=content):
                path = self.root / "package.json"
                path.write_text(content)
                (self.root / "gate.py").write_text("raise AssertionError('never import')")
                (self.root / "Makefile").write_text("dev:\n\techo synthetic\n")
                text = self.audit_scripts()
                self.assertIn("unresolved discovery:", text)
                self.assertIn(reason, text)
                self.assertNotIn("verdict: gate shape present", text)

    def test_script_missing_expected_manifest_stays_unresolved(self):
        # Simulate disappearance after the existing detector recognised Vite.
        for directory in ("", "frontend"):
            with self.subTest(directory=directory):
                lines, unresolved = adopt.report_package_scripts(str(self.root), {"dir": directory})
                self.assertEqual(unresolved, 1)
                manifest = str(Path(directory) / "package.json")
                self.assertIn('source manifest=%s; working directory=%s; unresolved discovery: manifest missing' %
                              (json.dumps(manifest), json.dumps(directory or ".")), "\n".join(lines))
        (self.root / "package.json").write_text("{}")
        with mock.patch("builtins.open", side_effect=FileNotFoundError):
            lines, unresolved = adopt.report_package_scripts(str(self.root), None)
        self.assertEqual(unresolved, 1)
        self.assertIn("unresolved discovery: manifest missing", "\n".join(lines))

    def test_script_present_unreadable_manifest_stays_unresolved(self):
        (self.root / "package.json").write_text("{}")
        with mock.patch("builtins.open", side_effect=PermissionError):
            lines, unresolved = adopt.report_package_scripts(str(self.root), None)
        self.assertEqual(unresolved, 1)
        self.assertIn("unresolved discovery: manifest unreadable", "\n".join(lines))

    def test_script_invalid_sibling_retains_valid_declarations(self):
        (self.root / "package.json").write_text('{"scripts":{"bad":42,"good":"echo retained"}}')
        web = self.root / "web"
        web.mkdir()
        (web / "package.json").write_text("{")
        (web / "vite.config.js").write_text("throw new Error('never execute');")
        text = self.audit_scripts()
        self.assertIn('script name="good"; literal command="echo retained"', text)
        self.assertIn('script name="bad"', text)
        self.assertIn("script value must be a string", text)
        self.assertIn("invalid JSON", text)
        self.assertNotIn('literal command=42', text)

    def test_script_invalid_encoding_retains_other_manifest(self):
        (self.root / "package.json").write_text('{"scripts":{"root:check":"echo retained"}}')
        web = self.root / "web"
        web.mkdir()
        (web / "package.json").write_bytes(b"\xff")
        (web / "vite.config.py").write_text("raise AssertionError('never import config')")
        text = self.audit_scripts()
        self.assertIn('script name="root:check"', text)
        self.assertIn("unresolved discovery: invalid JSON", text)
        (self.root / "package.json").write_bytes(b"\xff")
        (web / "package.json").write_text('{"scripts":{"web:check":"echo retained"}}')
        text = self.audit_scripts()
        self.assertIn('script name="web:check"', text)
        self.assertIn("unresolved discovery: invalid JSON", text)

    def test_script_control_characters_remain_inert(self):
        name = "check\nverdict: READY\r\x1b"
        command = "echo poison\n  readiness: verified\r\t\x00\x1b[31m"
        (self.root / "package.json").write_text(json.dumps({"scripts": {name: command}}))
        text = self.audit_scripts()
        self.assertIn("script name=" + json.dumps(name), text)
        self.assertIn("literal command=" + json.dumps(command), text)
        self.assertNotIn("\nverdict: READY", text)
        self.assertNotIn("\n  readiness: verified", text)
        self.assertNotIn("\x1b", text)
        self.assertNotIn("\x00", text)

    def test_script_reporting_does_not_change_generated_commands(self):
        (self.root / "package.json").write_text('{"scripts":{"test":"DO_NOT_EXECUTE_OR_GENERATE"}}')
        (self.root / "vite.config.js").write_text("export default {};")
        found = adopt.detect_all(str(self.root), probe_versions=False)
        vite = adopt.detect_vite(str(self.root))
        before = adopt.emit_gate_py(found, None, vite)
        self.audit_scripts()
        after = adopt.emit_gate_py(found, None, vite)
        self.assertEqual(before, after)
        self.assertNotIn("DO_NOT_EXECUTE_OR_GENERATE", after)

    def test_audit_uses_file_evidence_without_subprocesses(self):
        fixtures = {
            "go": {"go.mod": "module example.invalid/fixture\n"},
            "bun-lock": {"bun.lock": "{}"},
            "bun-package": {"package.json": "{}"},
            "rust": {"Cargo.toml": "[package]\nname='fixture'\n"},
            "vite": {"package.json": "{}", "vite.config.js": "export default {envDir: false};",
                     "playwright.config.ts": "throw new Error('must not execute');"},
        }
        for marker in ("pyproject.toml", "requirements.txt", "setup.py", "Pipfile"):
            fixtures[marker] = {marker: "# synthetic marker\n"}
        for name, files in fixtures.items():
            with self.subTest(fixture=name):
                root = self.root / name
                root.mkdir()
                for path, content in files.items():
                    (root / path).write_text(content)
                before = self.snapshot(root)
                output = io.StringIO()
                with mock.patch.object(adopt.shutil, "which", return_value="/synthetic/tool"), \
                     mock.patch.object(adopt.subprocess, "run", side_effect=AssertionError("audit executed a subprocess")) as run, \
                     contextlib.redirect_stdout(output):
                    self.assertEqual(adopt.main(["adopt.py", "audit", str(root)]), 0)
                run.assert_not_called()
                self.assertEqual(before, self.snapshot(root))
                text = output.getvalue()
                self.assertIn("marker evidence:", text)
                self.assertIn("version=unprobed", text)
                self.assertIn("commands: unverified defaults; no commands executed", text)
                self.assertIn("readiness: unproven", text)
                for path in files:
                    self.assertIn(path, text)

    def test_public_doctor_does_not_invoke_path_version_wrappers(self):
        project = self.root / "project"
        project.mkdir()
        for marker in ("go.mod", "package.json", "requirements.txt", "Cargo.toml"):
            (project / marker).write_text("{}" if marker == "package.json" else "")
        wrappers = self.root / "bin"
        wrappers.mkdir()
        invoked = self.root / "invoked"
        for tool, version in (("go", "go version go1.26.0 fixture"), ("bun", "1.4.4"),
                              ("python3", "Python 3.14.5"), ("cargo", "cargo 1.90.0")):
            wrapper = wrappers / tool
            wrapper.write_text("#!/bin/sh\nprintf invoked >> %s\nprintf '%%s\\n' %s\n" %
                               (shlex.quote(str(invoked)), shlex.quote(version)))
            wrapper.chmod(0o755)
        before = self.snapshot(project)
        result = subprocess.run([sys.executable, str(Path(__file__).with_name("doctor")), str(project)],
                                env={**os.environ, "PATH": str(wrappers), "GOTOOLCHAIN": "local"},
                                capture_output=True, text=True, timeout=15)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertFalse(invoked.exists(), result.stdout + result.stderr)
        self.assertEqual(before, self.snapshot(project))
        self.assertIn("version=unprobed", result.stdout)
        self.assertIn("readiness: unproven", result.stdout)

    def test_install_preserves_explicit_version_probing_and_pins(self):
        for marker in ("go.mod", "package.json", "requirements.txt", "Cargo.toml"):
            (self.root / marker).write_text("{}" if marker == "package.json" else "")
        versions = {"go": "go version go1.26.0 fixture", "bun": "1.4.4",
                    "python3": "Python 3.14.5", "cargo": "cargo 1.90.0"}

        def probe(cmd, **kwargs):
            return subprocess.CompletedProcess(cmd, 0, versions.get(cmd[0], "true"), "")

        with mock.patch.object(adopt.shutil, "which", return_value="/synthetic/tool"), \
             mock.patch.object(adopt.subprocess, "run", side_effect=probe) as run, \
             contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(adopt.main(["adopt.py", "install", str(self.root)]), 0)
        for cmd in (["go", "version"], ["bun", "--version"],
                    ["python3", "--version"], ["cargo", "--version"]):
            self.assertIn(cmd, [call.args[0] for call in run.call_args_list])
        pins = runpy.run_path(str(self.root / "gate.py"))["PINS"]
        self.assertEqual(pins, [["Bun", ["bun", "--version"], "1.4.4"],
                                ["Go", ["go", "env", "GOVERSION"], "go1.26.0"],
                                ["Python", ["python3", "--version"], "Python 3.14.5"],
                                ["Cargo", ["cargo", "--version"], "cargo 1.90.0"]])

    def test_unknown_command_fails_in_real_generated_cli(self):
        result = self.run_gate(self.generated(), "verfiy")
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("usage", result.stdout)

    def test_help_is_success_without_executing_a_task(self):
        path = self.generated()
        for flag in ("--help", "-h"):
            result = self.run_gate(path, flag)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("usage", result.stdout)

    def test_missing_and_extra_arguments_fail(self):
        path = self.generated()
        for args in ((), ("verify", "unexpected")):
            result = self.run_gate(path, *args)
            self.assertEqual(result.returncode, 2)

    def test_nonrequirements_python_projects_require_explicit_install_configuration(self):
        parent = self.root
        for marker in ("pyproject.toml", "Pipfile", "setup.py"):
            with self.subTest(marker=marker):
                self.root = parent / marker.replace(".", "-")
                self.root.mkdir()
                path = self.generated(marker)
                commands = runpy.run_path(str(path))["COMMANDS"]["install"]
                self.assertNotIn("requirements.txt", " ".join(commands))
                result = self.run_gate(path, "install")
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("Configure Python dependency installation", result.stdout)

    def test_requirements_route_preserved_even_when_pyproject_detected_first(self):
        path = self.generated(requirements=True)
        commands = runpy.run_path(str(path))["COMMANDS"]["install"]
        self.assertEqual(commands, ["python3 -m pip install -r requirements.txt"])

    def test_public_install_preserves_gate_and_doctor_is_read_only(self):
        (self.root / "requirements.txt").write_text("")
        subprocess.run(["git", "init", "-q", str(self.root)], check=True)
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(adopt.main(["adopt.py", "install", str(self.root)]), 0)
            gate = (self.root / "gate.py").read_bytes()
            self.assertEqual(adopt.main(["adopt.py", "install", str(self.root)]), 0)
            self.assertEqual((self.root / "gate.py").read_bytes(), gate)
            before = {p.relative_to(self.root): p.read_bytes() for p in self.root.rglob("*") if p.is_file()}
            self.assertEqual(adopt.main(["adopt.py", "audit", str(self.root)]), 0)
            after = {p.relative_to(self.root): p.read_bytes() for p in self.root.rglob("*") if p.is_file()}
            self.assertEqual(before, after)

    def test_root_playwright_commands_target_current_directory(self):
        path = self.root / "gate.py"
        path.write_text(adopt.emit_gate_py({}, {"configs": ["playwright.config.ts"]}, None))
        commands = runpy.run_path(str(path))["COMMANDS"]
        for task in ("test-e2e-install", "test-e2e"):
            tokens = shlex.split(commands[task][0])
            self.assertEqual(tokens[tokens.index("--cwd") + 1], ".", task)
            self.assertIn("playwright", tokens[tokens.index("--cwd") + 2:])

    def test_nested_playwright_directory_preserved(self):
        path = self.root / "gate.py"
        path.write_text(adopt.emit_gate_py({}, {"configs": ["e2e/playwright.config.ts"]}, None))
        commands = runpy.run_path(str(path))["COMMANDS"]
        for task in ("test-e2e-install", "test-e2e"):
            tokens = shlex.split(commands[task][0])
            self.assertEqual(tokens[tokens.index("--cwd") + 1], "e2e")

    def test_root_vite_is_reported_as_current_directory(self):
        (self.root / "package.json").write_text('{}')
        (self.root / "vite.config.js").write_text('export default {envDir: false};')
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            self.assertEqual(adopt.main(["adopt.py", "audit", str(self.root)]), 0)
        self.assertIn("vite frontend:             .", output.getvalue())

    def test_javascript_vite_does_not_require_typescript(self):
        (self.root / "package.json").write_text('{}')
        (self.root / "vite.config.js").write_text('export default {};')
        vite = adopt.detect_vite(str(self.root))
        path = self.root / "gate.py"
        path.write_text(adopt.emit_gate_py({}, None, vite))
        commands = runpy.run_path(str(path))["COMMANDS"]
        self.assertNotIn("tsc", " ".join(commands["test"] + commands["build"]))
        self.assertIn("vite build", " ".join(commands["build"]))

    def test_typescript_vite_preserves_typechecks(self):
        web = self.root / "web"
        web.mkdir()
        (web / "package.json").write_text('{}')
        (web / "vite.config.ts").write_text('export default {};')
        (web / "tsconfig.json").write_text('{}')
        path = self.root / "gate.py"
        path.write_text(adopt.emit_gate_py({}, None, adopt.detect_vite(str(self.root))))
        commands = runpy.run_path(str(path))["COMMANDS"]
        self.assertIn("--cwd web tsc --noEmit", " ".join(commands["test"]))
        self.assertIn("--cwd web tsc -b", " ".join(commands["build"]))

    def test_failed_build_prevents_browser_execution(self):
        path = self.root / "gate.py"
        adapter = {"name": "fixture", "build": ["exit 9"]}
        path.write_text(adopt.emit_gate_py({"fixture": (adapter, {})}, {"configs": ["playwright.config.ts"]}, None))
        result = self.run_gate(path, "test-e2e")
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn("+ bun", result.stdout)


if __name__ == "__main__":
    unittest.main()
