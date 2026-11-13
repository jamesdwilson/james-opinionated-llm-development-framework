"""Preservation characterizations through public doctor and explicit planning.

Native command strings are inert synthetic owner mappings. These contracts add
no language adapter and require no native SDK.
"""
import ast
import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import runpy
import socket
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

SPEC = importlib.util.spec_from_file_location("native_feedback_adopt", Path(__file__).with_name("adopt.py"))
assert SPEC is not None and SPEC.loader is not None
adopt = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(adopt)

CASES = (
    ("Haskell static", "example.cabal", "name: example\nversion: 0.1\n",
     ["cabal build all"], ["cabal test all"]),
    ("Erlang dynamic BEAM", "rebar.config", "{erl_opts, [debug_info]}.\n",
     ["rebar3 compile", "rebar3 dialyzer"], ["rebar3 eunit", "rebar3 ct"]),
    ("Gleam static BEAM", "gleam.toml", 'name = "example"\nversion = "0.1.0"\n',
     ["gleam build"], ["gleam test"]),
)


class NativeFeedbackPolicyContracts(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(prefix="native-feedback-")
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name).resolve()

    def fixture(self, index, case):
        label, marker, content, analysis, behavior = case
        root = self.root / str(index)
        root.mkdir()
        (root / marker).write_text(content)
        (root / "package.json").write_text(json.dumps({
            "name": "synthetic-native-project",
            "description": label,
            "scripts": {"check": analysis[0], "test": behavior[0]},
        }))
        commands = {"verify": analysis, "test": behavior, "build": []}
        (root / "gate.py").write_text(
            "# project-owned checks\nCOMMANDS = " + repr(commands) +
            "\nraise AssertionError('target gate must never execute')\n")
        (root / "gate.py").chmod(0o751)
        (root / "GATE.md").write_text("Project-owned guide. Retain native analysis and behavior.\n")
        (root / "Makefile").write_text("test:\n\t@echo project-owned\n")
        return root, commands

    def snapshot(self, root):
        return {path.relative_to(root): (path.read_bytes(), path.stat().st_mode & 0o7777)
                for path in root.rglob("*") if path.is_file()}

    @contextlib.contextmanager
    def no_execution(self):
        with mock.patch.object(subprocess, "run", side_effect=AssertionError("process forbidden")), \
             mock.patch.object(subprocess, "Popen", side_effect=AssertionError("process forbidden")), \
             mock.patch.object(os, "system", side_effect=AssertionError("shell forbidden")), \
             mock.patch.object(os, "execve", side_effect=AssertionError("exec forbidden")), \
             mock.patch.object(socket, "socket", side_effect=AssertionError("network forbidden")), \
             mock.patch.object(adopt, "_tool_version", side_effect=AssertionError("probe forbidden")):
            yield

    def plan(self, root, *args):
        output, errors = io.StringIO(), io.StringIO()
        with self.no_execution(), \
             mock.patch("builtins.exec", side_effect=AssertionError("target execution forbidden")), \
             contextlib.redirect_stdout(output), contextlib.redirect_stderr(errors):
            code = adopt.main(["adopt.py", "plan", str(root), *args])
        self.assertEqual((code, errors.getvalue()), (0, ""))
        return output.getvalue()

    def confirmation(self, output):
        return output.split("Confirmation SHA256: ", 1)[1].splitlines()[0]

    def commands(self, root):
        tree = ast.parse((root / "gate.py").read_bytes())
        assignment = next(node for node in tree.body if isinstance(node, ast.Assign))
        return ast.literal_eval(assignment.value)

    def test_public_doctor_labels_supply_no_adapter_or_readiness(self):
        for index, case in enumerate(CASES):
            with self.subTest(language=case[0]):
                root, _ = self.fixture(index, case)
                before = self.snapshot(root)
                output = io.StringIO()
                doctor = Path(__file__).with_name("doctor")
                # runpy executes only the public framework wrapper. Target files
                # remain data. Process/probe boundaries forbid native execution.
                with self.no_execution(), \
                     mock.patch.object(adopt.shutil, "which", side_effect=AssertionError("probe forbidden")), \
                     mock.patch.object(sys, "argv", [str(doctor), str(root)]), \
                     contextlib.redirect_stdout(output), self.assertRaises(SystemExit) as result:
                    runpy.run_path(str(doctor), run_name="__main__")
                self.assertEqual(result.exception.code, 0)
                text = output.getvalue()
                self.assertIn("readiness: unproven", text)
                self.assertIn("commands: unverified defaults; no commands executed", text)
                self.assertIn("Preserve existing gate.py", text)
                self.assertIn("--preview-gate", text)
                self.assertIn("--apply-gate FINGERPRINT", text)
                with self.no_execution():
                    self.assertEqual(adopt.detect_all(str(root), probe_versions=False), {})
                self.assertEqual(before, self.snapshot(root))

    def test_reviewed_apply_repeat_retains_analysis_behavior_and_native_owners(self):
        for index, case in enumerate(CASES):
            with self.subTest(language=case[0]):
                root, original_commands = self.fixture(index, case)
                before = self.snapshot(root)
                args = ("--command", "build", ".", "project-release-check")
                preview = self.plan(root, "--preview-gate", *args)
                self.assertEqual(before, self.snapshot(root))
                self.assertEqual(self.plan(root, "--preview-gate", *args), preview)
                self.plan(root, "--apply-gate", self.confirmation(preview), *args)
                commands = self.commands(root)
                self.assertEqual(commands["verify"], original_commands["verify"])
                self.assertEqual(commands["test"], original_commands["test"])
                self.assertEqual(commands["build"], ["(cd ./. && (\nproject-release-check\n))"])
                after = self.snapshot(root)
                for path, value in before.items():
                    if path != Path("gate.py"):
                        self.assertEqual(after[path], value)
                self.assertEqual(after[Path("gate.py")][1], 0o751)
                backups = list(root.glob("gate.py.reviewed-backup-sha256-*"))
                self.assertEqual(len(backups), 1)
                self.assertEqual((backups[0].read_bytes(), backups[0].stat().st_mode & 0o7777),
                                 before[Path("gate.py")])
                repeated = self.plan(root, "--preview-gate", *args)
                self.plan(root, "--apply-gate", self.confirmation(repeated), *args)
                self.assertEqual(after, self.snapshot(root))
                # Selecting an analysis role in the reviewed editor appends to
                # that role as well, retaining its project-owned commands.
                args = ("--command", "verify", ".", "project-extra-analysis")
                preview = self.plan(root, "--preview-gate", *args)
                self.plan(root, "--apply-gate", self.confirmation(preview), *args)
                self.assertEqual(self.commands(root)["verify"], original_commands["verify"] +
                                 ["(cd ./. && (\nproject-extra-analysis\n))"])
                self.assertEqual(self.commands(root)["test"], original_commands["test"])
                after = self.snapshot(root)
                repeated = self.plan(root, "--preview-gate", *args)
                self.plan(root, "--apply-gate", self.confirmation(repeated), *args)
                self.assertEqual(after, self.snapshot(root))

    def test_manual_selected_role_replacement_remains_explicit(self):
        for index, case in enumerate(CASES):
            with self.subTest(language=case[0]):
                root, original = self.fixture(index, case)
                before = self.snapshot(root)
                output = self.plan(root, "--command", "test", ".", "owner-reviewed-behavior")
                entries = ast.literal_eval("{" + output.split("```python\n", 1)[1].split("```", 1)[0] + "}")
                self.assertEqual(entries, {"test": ["(cd ./. && (\nowner-reviewed-behavior\n))"]})
                self.assertIn("Selected lists replace each selected task's whole list", output)
                self.assertIn("Review and merge required checks before applying", output)
                self.assertIn("explicitly supplied/unverified", output)
                merged = dict(original)
                merged.update(entries)
                self.assertEqual(merged["verify"], original["verify"])
                self.assertEqual(merged["test"], entries["test"])
                self.assertEqual(before, self.snapshot(root))


if __name__ == "__main__":
    unittest.main()
