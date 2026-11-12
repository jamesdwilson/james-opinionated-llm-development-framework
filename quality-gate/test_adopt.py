"""Bounded regressions for generated command dispatch and Python installation.
Run: python3 -m unittest discover -s quality-gate -p 'test_*.py' -v
"""
import contextlib
import importlib.util
import io
from pathlib import Path
import runpy
import shlex
import subprocess
import sys
import tempfile
import unittest

SPEC = importlib.util.spec_from_file_location("adopt", Path(__file__).with_name("adopt.py"))
assert SPEC is not None and SPEC.loader is not None
adopt = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(adopt)


class AdoptionContracts(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(prefix="gate-regression-")
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)

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

    def test_failed_build_prevents_browser_execution(self):
        path = self.root / "gate.py"
        adapter = {"name": "fixture", "build": ["exit 9"]}
        path.write_text(adopt.emit_gate_py({"fixture": (adapter, {})}, {"configs": ["playwright.config.ts"]}, None))
        result = self.run_gate(path, "test-e2e")
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn("+ bun", result.stdout)


if __name__ == "__main__":
    unittest.main()
