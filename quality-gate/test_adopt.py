"""Bounded regressions for generated command dispatch and Python installation.
Run: python3 -m unittest discover -s quality-gate -p 'test_*.py' -v
"""
import ast
import contextlib
import difflib
import gc
import importlib.util
import hashlib
import io
import json
import os
from pathlib import Path
import runpy
import shlex
import socket
import subprocess
import sys
import tempfile
import unittest
import warnings
from unittest import mock

SPEC = importlib.util.spec_from_file_location("adopt", Path(__file__).with_name("adopt.py"))
assert SPEC is not None and SPEC.loader is not None
adopt = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(adopt)


class AdoptionContracts(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(prefix="gate-regression-")
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name).resolve()

    def test_fixture_root_resolves_owned_directory_alias(self):
        with tempfile.TemporaryDirectory(dir=self.root) as owned:
            canonical = Path(owned).resolve()
            alias = self.root / "fixture-alias"
            alias.symlink_to(canonical, target_is_directory=True)
            directory = mock.Mock()
            directory.name = str(alias)
            # The real context owns cleanup; the facade never removes the alias.
            fixture = AdoptionContracts()
            try:
                with mock.patch.object(tempfile, "TemporaryDirectory", return_value=directory):
                    fixture.setUp()
                self.assertTrue(alias.is_symlink())
                self.assertNotEqual(Path(directory.name), canonical)
                self.assertEqual(fixture.root, canonical)
            finally:
                fixture.doCleanups()
            directory.cleanup.assert_called_once_with()
            self.assertTrue(canonical.is_dir())

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

    # Public reviewed syntax is fixed before implementation. All targets are synthetic.
    def reviewed(self, *args, target=None):
        output, errors = io.StringIO(), io.StringIO()
        with mock.patch.object(subprocess, "run", side_effect=AssertionError("execution forbidden")), \
             mock.patch.object(subprocess, "Popen", side_effect=AssertionError("execution forbidden")), \
             mock.patch.object(os, "system", side_effect=AssertionError("execution forbidden")), \
             mock.patch.object(socket, "socket", side_effect=AssertionError("network forbidden")), \
             mock.patch("builtins.exec", side_effect=AssertionError("target execution forbidden")), \
             contextlib.redirect_stdout(output), contextlib.redirect_stderr(errors):
            code = adopt.main(["adopt.py", "plan", str(self.root if target is None else target), *args])
        return code, output.getvalue(), errors.getvalue()

    def confirmation(self, output):
        return output.split("Confirmation SHA256: ", 1)[1].splitlines()[0]

    def test_reviewed_display_direct_quotes_multiline_and_no_writes(self):
        path = self.root / 'gate.py'
        path.write_text('# review context\nCOMMANDS = {\n    "test": ["old-check"],\n}\n')
        before = self.snapshot(self.root)
        args = ('--command', 'test', '.', 'printf "hello"\nprintf \'world\'')
        code, output, errors = self.reviewed('--preview-gate', *args)
        self.assertEqual((code, errors), (0, ''))
        self.assertIn('Human review diff (display-only; do not paste/apply):\n', output)
        display = output.split('Human review diff (display-only; do not paste/apply):\n', 1)[1].split(
            'Exact unified diff as a JSON-escaped UTF-8 string (decode to recover diff bytes):\n', 1)[0]
        self.assertIn('| --- a/gate.py\n| +++ b/gate.py\n| @@ ', display)
        self.assertIn('|  # review context\n', display)
        self.assertIn('| -    "test": ["old-check"],\n', display)
        self.assertIn('| +    "test": ["old-check", ', display)
        self.assertIn('printf "hello"', display)
        self.assertIn(r"\\nprintf", display)
        self.assertNotIn(r'\"hello\"', display)
        self.assertIn('LF gives layout; backslashes doubled; other controls/non-ASCII use \\uXXXX/\\UXXXXXXXX.', display)
        self.assertEqual(before, self.snapshot(self.root))
        self.assertEqual(output.splitlines()[-1], 'Confirmation SHA256: ' + self.confirmation(output))

    def test_reviewed_display_named_escapes_and_confirmation_spoofing(self):
        self.literal_gate()
        cases = (
            ('CR', '\r', r'\u000d'), ('tab', '\t', r'\u0009'),
            ('ESC', '\x1b', r'\u001b'), ('NUL', '\0', r'\u0000'),
            ('C0', '\x01\x1f', r'\u0001\u001f'), ('DEL', '\x7f', r'\u007f'),
            ('C1', '\x80\x85\x9f', r'\u0080\u0085\u009f'),
            ('nonASCII', 'é雪', r'\u00e9\u96ea'), ('astral', '😀', r'\U0001f600'),
            ('bidi', '\u202e\u2066\u2069', r'\u202e\u2066\u2069'),
            ('backslash', '\\', r'\\'), ('literal escape', r'\u001b', r'\\u001b'),
            ('literal astral escape', r'\U0001f600', r'\\U0001f600'),
            ('LF label', '\nConfirmation SHA256: forged\n', '\n| Confirmation SHA256: forged\n| '),
        )
        for name, text, escaped in cases:
            with self.subTest(name=name):
                diff = ('+before' + text + 'after\n').encode('utf-8')
                with mock.patch.object(adopt.difflib, 'diff_bytes', return_value=iter([diff])):
                    code, output, errors = self.reviewed('--preview-gate', '--command', 'test', '.', 'true')
                self.assertEqual((code, errors), (0, ''))
                self.assertIn('Human review diff (display-only; do not paste/apply):\n', output)
                display = output.split('Human review diff (display-only; do not paste/apply):\n', 1)[1].split(
                    'Exact unified diff as a JSON-escaped UTF-8 string (decode to recover diff bytes):\n', 1)[0]
                self.assertIn('| +before' + escaped + 'after\n', display)
                self.assertTrue(all(c == '\n' or 32 <= ord(c) <= 126 for c in output))
                self.assertEqual(sum(line.startswith('Confirmation SHA256: ') for line in output.splitlines()), 1)
                exact = output.split('recover diff bytes):\n', 1)[1].splitlines()
                self.assertEqual(json.loads(exact[0]).encode('utf-8'), diff)
                self.assertRegex(exact[1], r'^Confirmation SHA256: [0-9a-f]{64}$')

    def test_reviewed_display_exact_binding_and_empty_view(self):
        path = self.literal_gate()
        original = path.read_bytes()
        selections = [['test', '.', 'true']]
        commands = {'test': ['(cd ./. && (\ntrue\n))']}
        result = adopt.reviewed_gate_bytes(original, commands)
        def base_digest(content, proposed):
            binding = json.dumps([str(path), content.hex(), path.stat().st_mode & 0o7777,
                                  selections, proposed.hex()], ensure_ascii=True, separators=(',', ':')).encode('ascii')
            return hashlib.sha256(binding).hexdigest()
        args = ('--command', 'test', '.', 'true')
        preview = self.reviewed('--preview-gate', *args)
        self.assertEqual(self.confirmation(preview[1]), base_digest(original, result))
        self.assertEqual(self.reviewed('--apply-gate', self.confirmation(preview[1]), *args)[0], 0)
        before = self.snapshot(self.root)
        empty = self.reviewed('--preview-gate', *args)
        self.assertEqual((empty[0], empty[2]), (0, ''))
        self.assertIn('| (no changes)\n', empty[1])
        self.assertNotIn('| --- ', empty[1])
        self.assertIn('recover diff bytes):\n""\nConfirmation SHA256: ', empty[1])
        self.assertEqual(self.confirmation(empty[1]), base_digest(result, result))
        self.assertEqual(before, self.snapshot(self.root))

    def literal_gate(self):
        path = self.root / "gate.py"
        path.write_bytes(b"# surrounding \xc3\xa9\r\nCOMMANDS = {'test': ['local-check',], 'build': [], 'verify': ['required']} # keep\r\n# tail\r\n")
        return path

    def backup_path(self, original, mode):
        # Public name contract, independent of the production implementation.
        return self.root / ('gate.py.reviewed-backup-sha256-' +
                            hashlib.sha256(original).hexdigest() + '-mode-' + format(mode, '04o'))

    def retained_metadata(self, path):
        metadata = path.stat()
        return (metadata.st_ino, metadata.st_mode, metadata.st_mtime_ns,
                metadata.st_ctime_ns, metadata.st_size)

    def test_reviewed_successive_changes_reuse_modes_and_legacy(self):
        path = self.literal_gate()
        legacy = self.root / 'gate.py.reviewed-backup'
        legacy.write_bytes(b'legacy history')
        legacy.chmod(0o640)
        history = []
        for index, mode in enumerate((0o751, 0o640, 0o700)):
            path.chmod(mode)
            original = path.read_bytes()
            args = ('--command', 'test', '.', 'revision-' + str(index))
            preview = self.reviewed('--preview-gate', *args)
            result = self.reviewed('--apply-gate', self.confirmation(preview[1]), *args)
            self.assertEqual(result[0], 0, result)
            backup = self.backup_path(original, mode)
            self.assertIn(ascii(str(backup)), result[1])
            history.append((backup, original, mode, self.retained_metadata(backup)))
            self.assertEqual(path.stat().st_mode & 0o7777, mode)
            self.assertFalse((self.root / 'gate.py.reviewed-tmp').exists())
            for retained, content, permissions, metadata in history:
                self.assertEqual(retained.read_bytes(), content)
                self.assertEqual(self.retained_metadata(retained), metadata)
                self.assertEqual(retained.stat().st_mode & 0o7777, permissions)
        self.assertEqual(len(list(self.root.glob('gate.py.reviewed-backup-sha256-*'))), 3)
        self.assertEqual(legacy.read_bytes(), b'legacy history')
        self.assertEqual(legacy.stat().st_mode & 0o7777, 0o640)
        # Controlled restoration reuses the exact backup without touching its inode/metadata.
        backup, original, mode, metadata = history[0]
        path.write_bytes(original)
        path.chmod(mode)
        args = ('--command', 'test', '.', 'restored-change')
        preview = self.reviewed('--preview-gate', *args)
        self.assertEqual(self.reviewed('--apply-gate', self.confirmation(preview[1]), *args)[0], 0)
        self.assertEqual(self.retained_metadata(backup), metadata)
        self.assertEqual(backup.read_bytes(), original)
        # Same original bytes, only mode differs: a separate recoverable backup.
        path.write_bytes(original)
        path.chmod(0o754)
        preview = self.reviewed('--preview-gate', *args)
        self.assertEqual(self.reviewed('--apply-gate', self.confirmation(preview[1]), *args)[0], 0)
        self.assertEqual(self.backup_path(original, 0o754).read_bytes(), original)
        self.assertEqual(self.backup_path(original, 0o754).stat().st_mode & 0o7777, 0o754)
        self.assertEqual(self.retained_metadata(backup), metadata)
        self.assertEqual(len(list(self.root.glob('gate.py.reviewed-backup-sha256-*'))), 4)

    def test_reviewed_repeat_changes_without_legacy_relocation(self):
        path = self.literal_gate()
        path.chmod(0o644)
        originals = []
        for command in ('second-required-check', 'third-required-check', 'fourth-required-check'):
            originals.append(path.read_bytes())
            args = ('--command', 'test', '.', command)
            preview = self.reviewed('--preview-gate', *args)
            result = self.reviewed('--apply-gate', self.confirmation(preview[1]), *args)
            self.assertEqual(result[0], 0, result)
        for original in originals:
            self.assertEqual(self.backup_path(original, 0o644).read_bytes(), original)

    def test_reviewed_multi_task_preservation_and_idempotence(self):
        path = self.literal_gate()
        path.chmod(0o751)
        before = path.read_bytes()
        args = ("--command", "test", ".", "new-check", "--command", "build", ".", "build-check")
        preview = self.reviewed("--preview-gate", *args)
        self.assertEqual((preview[0], preview[2]), (0, ""))
        self.assertEqual(preview, self.reviewed("--preview-gate", *args))
        self.assertEqual(path.read_bytes(), before)
        self.assertIn("--- ", preview[1])
        self.assertIn("+++ ", preview[1])
        fingerprint = self.confirmation(preview[1])
        self.assertRegex(fingerprint, r"^[0-9a-f]{64}$")
        self.assertEqual(self.reviewed("--apply-gate", fingerprint, *args)[0], 0)
        after = path.read_bytes()
        self.assertTrue(after.startswith(b"# surrounding \xc3\xa9\r\n"))
        self.assertTrue(after.endswith(b" # keep\r\n# tail\r\n"))
        self.assertIn(b"'verify': ['required']", after)
        values = ast.literal_eval(ast.parse(after).body[0].value)
        self.assertEqual(values['test'], ['local-check', '(cd ./. && (\nnew-check\n))'])
        self.assertEqual(values['build'], ['(cd ./. && (\nbuild-check\n))'])
        backup = self.backup_path(before, 0o751)
        self.assertEqual(backup.read_bytes(), before)
        self.assertEqual(path.stat().st_mode & 0o7777, 0o751)
        self.assertEqual(backup.stat().st_mode & 0o7777, 0o751)
        self.assertEqual(self.reviewed('--apply-gate', fingerprint, *args)[0], 2)
        repeated = self.reviewed('--preview-gate', *args)
        self.assertNotIn('--- ', repeated[1])
        (self.root / 'gate.py.reviewed-tmp').write_bytes(b'incomplete but no-change needs no preparation')
        snapshot = self.snapshot(self.root)
        self.assertEqual(self.reviewed('--apply-gate', self.confirmation(repeated[1]), *args)[0], 0)
        self.assertEqual(snapshot, self.snapshot(self.root))

    def test_reviewed_confirmation_and_stale_refusal(self):
        path = self.literal_gate()
        args = ('--command', 'test', '.', 'true')
        preview = self.reviewed('--preview-gate', *args)
        self.assertEqual(preview[0], 0, preview)
        fingerprint = self.confirmation(preview[1])
        for options in [('--apply-gate',), ('--apply-gate', 'bad'),
                        ('--apply-gate', '0' * 64), ('--apply-gate', fingerprint, '--preview-gate')]:
            with self.subTest(options=options):
                before = self.snapshot(self.root)
                self.assertEqual(self.reviewed(*options, *args)[0], 2)
                self.assertEqual(before, self.snapshot(self.root))
        for changed in [('test', '.', 'false'), ('build', '.', 'true')]:
            before = self.snapshot(self.root)
            self.assertEqual(self.reviewed('--apply-gate', fingerprint, '--command', *changed)[0], 2)
            self.assertEqual(before, self.snapshot(self.root))
        path.write_bytes(path.read_bytes() + b'# user edit\n')
        before = self.snapshot(self.root)
        self.assertEqual(self.reviewed('--apply-gate', fingerprint, *args)[0], 2)
        self.assertEqual(before, self.snapshot(self.root))

    def test_reviewed_ast_rejections_and_decoys(self):
        path = self.root / 'gate.py'
        invalid = ["COMMANDS = {", "COMMANDS = dict(test=[])",
                   "COMMANDS = {'test': []}\nCOMMANDS = {'test': []}",
                   "COMMANDS = {'test': [], 'test': []}", "COMMANDS = {'other': []}",
                   "COMMANDS = {1: []}", "COMMANDS = {'test': 'true'}",
                   "COMMANDS = {'test': [1]}", "COMMANDS = {'test': ('true',)}",
                   "COMMANDS = {'test': [f'true']}", "COMMANDS: dict = {'test': []}",
                   "COMMANDS = other = {'test': []}", "if True:\n COMMANDS = {'test': []}",
                   "COMMANDS = {'test': []}\nCOMMANDS['test'] = []",
                   "COMMANDS = {'test': []}\nCOMMANDS.update(test=[])",
                   "COMMANDS = {'test': []}\nCOMMANDS['test'].append('false')",
                   "COMMANDS = {'test': []}\nCOMMANDS |= {}",
                   "# COMMANDS = {'test': []}\nx = \"COMMANDS = {'test': []}\"",
                   "import re\nx = r\"COMMANDS\\s*=.*\"",
                   "COMMANDS = {'build': []}"]
        for source in invalid:
            with self.subTest(source=source):
                path.write_text(source)
                before = self.snapshot(self.root)
                result = self.reviewed('--preview-gate', '--command', 'test', '.', 'true')
                self.assertEqual(result[0], 2, result)
                self.assertNotIn('Confirmation SHA256', result[1])
                self.assertEqual(before, self.snapshot(self.root))
        path.write_text("# COMMANDS = {}\nx = \"COMMANDS = {}\"\nr = r'COMMANDS.*='\n"
                        "COMMANDS = {'test': []}\nraise AssertionError('inert')\n")
        args = ('--command', 'test', '.', 'echo NEVER_EXECUTE')
        result = self.reviewed('--preview-gate', *args)
        self.assertEqual(result[0], 0, result)
        self.assertEqual(self.reviewed('--apply-gate', self.confirmation(result[1]), *args)[0], 0)

    def reviewed_binding_cases(self):
        cases = [
            ('import-alias', 'import os as COMMANDS'),
            ('from-import', 'from owned import COMMANDS'),
            ('from-alias', 'from owned import other as COMMANDS'),
            ('relative-from', 'from .owned import COMMANDS'),
            ('unaliased-import', 'import COMMANDS'),
            ('dotted-import', 'import COMMANDS.child'),
            ('wildcard-import', 'from owned import *'),
            ('function', 'def COMMANDS(): pass'),
            ('async-function', 'async def COMMANDS(): pass'),
            ('class', 'class COMMANDS: pass'),
            ('exception', 'try: pass\nexcept Exception as COMMANDS: pass'),
            ('positional-arg', 'def f(COMMANDS): pass'),
            ('posonly-arg', 'def f(COMMANDS, /): pass'),
            ('kwonly-arg', 'def f(*, COMMANDS): pass'),
            ('vararg', 'def f(*COMMANDS): pass'),
            ('kwarg', 'def f(**COMMANDS): pass'),
            ('lambda-arg', 'f = lambda COMMANDS: None'),
            ('nested-definition', 'def outer():\n def COMMANDS(): pass'),
            ('nested-import', 'def outer():\n import os as COMMANDS'),
            ('unreachable-class', 'if False:\n class COMMANDS: pass'),
            ('global-reference', 'def f():\n global COMMANDS'),
            ('nonlocal-reference', 'def f():\n COMMANDS = {}\n def g():\n  nonlocal COMMANDS'),
            ('assignment', 'COMMANDS = {}'),
            ('annotated', 'COMMANDS: dict'),
            ('augmented', 'COMMANDS |= {}'),
            ('delete', 'del COMMANDS'),
            ('loop', 'for COMMANDS in []: pass'),
            ('comprehension', 'x = [0 for COMMANDS in []]'),
            ('with-target', 'with manager() as COMMANDS: pass'),
            ('named-expression', 'if (COMMANDS := {}): pass'),
            ('alias', 'other = COMMANDS'),
        ]
        if hasattr(ast, 'MatchAs'):
            cases += [('match-as', 'match subject:\n case COMMANDS: pass'),
                      ('match-nested-as', 'match subject:\n case [other] as COMMANDS: pass'),
                      ('match-star', 'match subject:\n case [*COMMANDS]: pass'),
                      ('match-rest', 'match subject:\n case {"key": other, **COMMANDS}: pass')]
        if hasattr(ast, 'TryStar'):
            cases += [('exception-group', 'try: pass\nexcept* Exception as COMMANDS: pass')]
        if hasattr(ast, 'TypeAlias'):
            cases += [('type-alias', 'type COMMANDS = int'),
                      ('typevar', 'def f[COMMANDS](): pass'),
                      ('paramspec', 'def f[**COMMANDS](): pass'),
                      ('typevartuple', 'class C[*COMMANDS]: pass'),
                      ('alias-typevar', 'type Other[COMMANDS] = int')]
        return cases

    def test_reviewed_binding_guard_refusal(self):
        for name, suffix in self.reviewed_binding_cases():
            with self.subTest(binding=name):
                source = ("COMMANDS = {'test': ['exit 7']}\n" + suffix + '\n').encode()
                # Parse first: malformed test syntax must not masquerade as refusal.
                ast.parse(source)
                diagnostic = 'exactly one simple' if name == 'assignment' else 'unsupported COMMANDS'
                with self.assertRaisesRegex(ValueError, diagnostic):
                    adopt.reviewed_gate_bytes(source, {'test': ['selected']})

    def test_reviewed_binding_public_preview_refusal(self):
        self.check_reviewed_binding_public_refusal(apply=False)

    def test_reviewed_binding_public_apply_refusal(self):
        self.check_reviewed_binding_public_refusal(apply=True)

    def check_reviewed_binding_public_refusal(self, apply):
        command = 'echo SELECTED_UNEXECUTED > selected-marker'
        rendered = '(cd ./. && (\n' + command + '\n))'
        for name, suffix in self.reviewed_binding_cases():
            with self.subTest(binding=name):
                target = self.root / name
                target.mkdir()
                path = target / 'gate.py'
                original = ("# keep é\nCOMMANDS = {'test': ['exit 7']}\n" + suffix +
                            "\nfor cmd in COMMANDS.get('test', []):\n pass\n# tail\n").encode()
                path.write_bytes(original)
                (target / 'owned.py').write_text("COMMANDS = {'test': ['exit 9']}\n")
                # Exact vulnerable insertion and fingerprint, independent of the guard.
                # RED verifies this confirms a changing apply, not a mismatch refusal.
                result = original.replace(b"['exit 7']", ("['exit 7', " + ascii(rendered) + ']').encode(), 1)
                binding = json.dumps([str(path.resolve()), original.hex(), path.stat().st_mode & 0o7777,
                                      [('test', '.', command)], result.hex()],
                                     ensure_ascii=True, separators=(',', ':')).encode('ascii')
                fingerprint = hashlib.sha256(binding).hexdigest()
                options = ('--apply-gate', fingerprint) if apply else ('--preview-gate',)
                before = self.snapshot(target)
                response = self.reviewed(*options, '--command', 'test', '.', command, target=target)
                # Check every invariant even when the public status is wrong in RED.
                with self.subTest(invariant='status'):
                    self.assertEqual(response[0], 2, response)
                with self.subTest(invariant='diagnostic'):
                    self.assertIn('exactly one simple' if name == 'assignment' else 'unsupported COMMANDS', response[2])
                with self.subTest(invariant='no-preview'):
                    self.assertEqual(response[1], '')
                with self.subTest(invariant='no-writes'):
                    self.assertEqual(before, self.snapshot(target))
                self.assertFalse((target / 'selected-marker').exists())

    def test_reviewed_binding_inert_decoys_and_unrelated_names(self):
        path = self.root / 'gate.py'
        original = ("# def COMMANDS(): pass\ntext = 'from owned import COMMANDS'\n"
                    "regex = r'COMMANDS.*='\nCOMMANDS = {'test': ['exit 7'], 'build': ['exit 9']}\n"
                    "import owned.COMMANDS\nfrom owned import COMMANDS as other\n"
                    "import owned as unrelated\ndef f(other, /, *args, flag=None, **kwargs):\n"
                    " global unrelated\nclass Other: pass\n"
                    "try: pass\nexcept Exception as other: pass\n")
        if hasattr(ast, 'MatchAs'):
            original += 'match subject:\n case {"COMMANDS": other, **rest}: pass\n'
        if hasattr(ast, 'TypeAlias'):
            original += 'type OtherAlias[T] = T\n'
        original = original.encode()
        path.write_bytes(original)
        command = 'echo SELECTED_UNEXECUTED > selected-marker'
        args = ('--command', 'test', '.', command)
        preview = self.reviewed('--preview-gate', *args)
        self.assertEqual((preview[0], preview[2]), (0, ''), preview)
        self.assertEqual(path.read_bytes(), original)
        self.assertEqual(self.reviewed('--apply-gate', self.confirmation(preview[1]), *args)[0], 0)
        rendered = '(cd ./. && (\n' + command + '\n))'
        self.assertEqual(path.read_bytes(), original.replace(b"['exit 7']",
                         ("['exit 7', " + ascii(rendered) + ']').encode(), 1))
        self.assertEqual(self.backup_path(original, path.stat().st_mode & 0o7777).read_bytes(), original)
        self.assertFalse((self.root / 'selected-marker').exists())

    def test_reviewed_target_and_directory_constraints(self):
        path = self.literal_gate()
        (self.root / 'outside').symlink_to(self.root.parent, target_is_directory=True)
        for task, directory, command in [('unknown', '.', 'true'), ('test', '..', 'true'),
                                          ('test', str(self.root), 'true'), ('test', 'outside', 'true'),
                                          ('test', 'missing', 'true'), ('test', '.', ' '),
                                          ('test', '', 'true'), ('test', '.', 'a\x00b')]:
            with self.subTest(task=task, directory=directory, command=command):
                before = path.read_bytes()
                self.assertEqual(self.reviewed('--preview-gate', '--command', task, directory, command)[0], 2)
                self.assertEqual(path.read_bytes(), before)
        for target in ['', self.root / 'missing', path]:
            self.assertEqual(self.reviewed('--preview-gate', '--command', 'test', '.', 'true', target=target)[0], 2)
        path.rename(self.root / 'original.py')
        args = ('--preview-gate', '--command', 'test', '.', 'true')
        self.assertEqual(self.reviewed(*args)[0], 2)
        path.symlink_to(self.root / 'original.py')
        self.assertEqual(self.reviewed(*args)[0], 2)
        path.unlink()
        path.mkdir()
        self.assertEqual(self.reviewed(*args)[0], 2)
        path.rmdir()
        os.mkfifo(path)
        self.assertEqual(self.reviewed(*args)[0], 2)

    def test_reviewed_backup_and_temp_collision(self):
        path = self.literal_gate()
        path.chmod(0o751)
        original = path.read_bytes()
        backup = self.backup_path(original, 0o751)
        args = ('--command', 'test', '.', 'true')
        preview = self.reviewed('--preview-gate', *args)
        self.assertEqual(preview[0], 0, preview)
        # Replaces fixed-backup collision policy: computed collisions still fail closed.
        for kind in ('wrong-content', 'wrong-mode', 'directory', 'symlink', 'fifo', 'temp'):
            with self.subTest(kind=kind):
                collision = self.root / 'gate.py.reviewed-tmp' if kind == 'temp' else backup
                if kind == 'directory':
                    collision.mkdir()
                elif kind == 'symlink':
                    collision.symlink_to(path)
                elif kind == 'fifo':
                    os.mkfifo(collision)
                else:
                    collision.write_bytes(original if kind == 'wrong-mode' else b'owned')
                    collision.chmod(0o751 if kind == 'wrong-content' else 0o600)
                collision_metadata = collision.lstat()
                before = self.snapshot(self.root) if kind != 'fifo' else None
                result = self.reviewed('--apply-gate', self.confirmation(preview[1]), *args)
                self.assertEqual(result[0], 2, result)
                self.assertEqual(path.read_bytes(), original)
                self.assertEqual(collision.lstat().st_mode, collision_metadata.st_mode)
                self.assertEqual(collision.lstat().st_ino, collision_metadata.st_ino)
                self.assertEqual(path.stat().st_mode & 0o7777, 0o751)
                if before is not None:
                    self.assertEqual(self.snapshot(self.root), before)
                if kind == 'temp':
                    self.assertIn('inspect', result[2].lower())
                    self.assertFalse(backup.exists())
                collision.rename(self.root / ('retained-' + kind))

    def test_reviewed_preparation_flush_failure_preserves_original(self):
        path = self.literal_gate()
        original = path.read_bytes()
        mode = path.stat().st_mode & 0o7777
        args = ('--command', 'test', '.', 'true')
        preview = self.reviewed('--preview-gate', *args)
        real_fsync = os.fsync
        calls = 0
        def fail_temporary_flush(fd):
            nonlocal calls
            calls += 1
            if calls == 2:
                raise OSError('injected temporary flush failure')
            real_fsync(fd)
        with mock.patch.object(os, 'fsync', side_effect=fail_temporary_flush), \
             mock.patch.object(os, 'replace', side_effect=AssertionError('no replacement after failed flush')):
            result = self.reviewed('--apply-gate', self.confirmation(preview[1]), *args)
        self.assertEqual(result[0], 2, result)
        self.assertEqual(calls, 2)
        self.assertEqual(path.read_bytes(), original)
        self.assertEqual(path.stat().st_mode & 0o7777, mode)
        self.assertEqual(self.backup_path(original, mode).read_bytes(), original)
        self.assertEqual(self.backup_path(original, mode).stat().st_mode & 0o7777, mode)
        self.assertTrue((self.root / 'gate.py.reviewed-tmp').is_file())
        before = self.snapshot(self.root)
        self.assertEqual(self.reviewed('--apply-gate', self.confirmation(preview[1]), *args)[0], 2)
        self.assertEqual(self.snapshot(self.root), before)

    def test_reviewed_exclusive_backup_create_race(self):
        path = self.literal_gate()
        original = path.read_bytes()
        backup = self.backup_path(original, path.stat().st_mode & 0o7777)
        args = ('--command', 'test', '.', 'true')
        preview = self.reviewed('--preview-gate', *args)
        real_open = os.open
        def collide(destination, flags, *rest):
            if destination == str(backup):
                backup.write_bytes(b'racing owner')
            return real_open(destination, flags, *rest)
        with mock.patch.object(os, 'open', side_effect=collide):
            result = self.reviewed('--apply-gate', self.confirmation(preview[1]), *args)
        self.assertEqual(result[0], 2, result)
        self.assertEqual(path.read_bytes(), original)
        self.assertEqual(backup.read_bytes(), b'racing owner')
        self.assertFalse((self.root / 'gate.py.reviewed-tmp').exists())

    def test_reviewed_failure_before_replace_and_final_conflict(self):
        path = self.literal_gate()
        args = ('--command', 'test', '.', 'true')
        preview = self.reviewed('--preview-gate', *args)
        self.assertEqual(preview[0], 0, preview)
        before = path.read_bytes()
        with mock.patch.object(os, 'replace', side_effect=OSError('injected before replace')):
            self.assertEqual(self.reviewed('--apply-gate', self.confirmation(preview[1]), *args)[0], 2)
        self.assertEqual(path.read_bytes(), before)
        self.assertEqual(self.backup_path(before, path.stat().st_mode & 0o7777).read_bytes(), before)
        # The fixed incomplete temporary file still blocks retry; backup remains reusable.
        snapshot = self.snapshot(self.root)
        refused = self.reviewed('--apply-gate', self.confirmation(preview[1]), *args)
        self.assertEqual(refused[0], 2)
        self.assertIn('inspect', refused[2].lower())
        self.assertEqual(snapshot, self.snapshot(self.root))
        temporary = self.root / 'gate.py.reviewed-tmp'
        temporary.rename(self.root / 'gate.py.reviewed-tmp.retained')
        real_fsync = os.fsync
        def edit_during_preparation(fd):
            real_fsync(fd)
            path.write_bytes(before + b'# concurrent ordinary edit\n')
        with mock.patch.object(os, 'fsync', side_effect=edit_during_preparation), \
             mock.patch.object(os, 'replace', side_effect=AssertionError('must refuse conflict')):
            self.assertEqual(self.reviewed('--apply-gate', self.confirmation(preview[1]), *args)[0], 2)
        self.assertEqual(path.read_bytes(), before + b'# concurrent ordinary edit\n')

    def test_reviewed_generated_gate_native_and_fail_first(self):
        path = self.root / 'gate.py'
        # Existing local commands are explicitly owned fixture checks.
        source = adopt.emit_gate_py({}, None, None)
        source = source.replace('echo no test adapter matched & exit 1', 'printf local > local.txt')
        path.write_text(source)
        tests = self.root / 'tests'
        tests.mkdir()
        native = tests / 'test_native.py'
        native.write_text('import unittest\nclass Native(unittest.TestCase):\n def test_arithmetic(self): self.assertEqual(2+2, 4)\n')
        args = ('--command', 'test', '.', shlex.quote(sys.executable) + ' -B -I -m unittest discover -s tests -v')
        preview = self.reviewed('--preview-gate', *args)
        self.assertEqual(preview[0], 0, preview)
        self.assertEqual(self.reviewed('--apply-gate', self.confirmation(preview[1]), *args)[0], 0)
        result = self.run_gate(path, 'test')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('Ran 1 test', result.stderr)
        self.assertEqual((self.root / 'local.txt').read_text(), 'local')
        native.write_text(native.read_text().replace('2+2, 4', '2+2, 5'))
        result = self.run_gate(path, 'test')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('FAILED (failures=1)', result.stderr)
        # An original failure must still stop before the appended native test.
        path.write_text(path.read_text().replace('printf local > local.txt', 'exit 7'))
        result = self.run_gate(path, 'test')
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn('Ran 1 test', result.stderr)

    def test_reviewed_parentheses_comments_and_exact_diff(self):
        args = ('--command', 'test', '.', 'true', '--command', 'test', '.', 'true')
        sources = [b"COMMANDS = {'test': [('old')]}",
                   b"COMMANDS = {'test': ['old' # keep\n]}",
                   b"COMMANDS = {'test': ['old', # keep\n]}",
                   b"COMMANDS = {'test': [ # empty\n]}",
                   "x='é'; COMMANDS = {'test': ['é']}".encode(),
                   b"\xef\xbb\xbfCOMMANDS = {'test': []}\r\n"]
        for index, before in enumerate(sources):
            with self.subTest(source=before):
                case_root = self.root / ('literal-' + str(index))
                case_root.mkdir()
                path = case_root / 'gate.py'
                path.write_bytes(before)
                preview = self.reviewed('--preview-gate', *args, target=case_root)
                self.assertEqual(preview[0], 0, preview)
                self.assertEqual(self.reviewed('--apply-gate', self.confirmation(preview[1]), *args, target=case_root)[0], 0)
                tree = ast.parse(path.read_bytes())
                assignment = next(node for node in tree.body if isinstance(node, ast.Assign)
                                  and isinstance(node.targets[0], ast.Name) and node.targets[0].id == 'COMMANDS')
                values = ast.literal_eval(assignment.value)['test']
                self.assertEqual(values[-1], '(cd ./. && (\ntrue\n))')
                self.assertEqual(len(values), 1 if index in [3, 5] else 2)
                self.assertTrue(all(isinstance(value, str) for value in values))
                # The decoded diff must describe precisely the bytes actually applied.
                diff = list(difflib.diff_bytes(difflib.unified_diff, before.splitlines(keepends=True),
                            path.read_bytes().splitlines(keepends=True), fromfile=b'a/gate.py', tofile=b'b/gate.py'))
                exact = b''.join(line if line.endswith(b'\n') else line + b'\n\\ No newline at end of file\n'
                                 for line in diff)
                line = preview[1].split('recover diff bytes):\n', 1)[1].splitlines()[0]
                self.assertEqual(json.loads(line).encode('utf-8'), exact)

    def test_reviewed_mode_and_target_binding(self):
        path = self.literal_gate()
        args = ('--command', 'test', '.', 'true')
        preview = self.reviewed('--preview-gate', *args)
        self.assertEqual(preview[0], 0, preview)
        fingerprint = self.confirmation(preview[1])
        alias = self.root / 'alias'
        alias.symlink_to(self.root, target_is_directory=True)
        self.assertEqual(self.reviewed('--preview-gate', *args, target=alias), preview)
        other = self.root / 'other'
        other.mkdir()
        (other / 'gate.py').write_bytes(path.read_bytes())
        self.assertEqual(self.reviewed('--apply-gate', fingerprint, *args, target=other)[0], 2)
        path.chmod(0o700 if path.stat().st_mode & 0o777 != 0o700 else 0o600)
        before = self.snapshot(self.root)
        self.assertEqual(self.reviewed('--apply-gate', fingerprint, *args)[0], 2)
        self.assertEqual(before, self.snapshot(self.root))

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

    def public_guidance(self, root=None):
        root = self.root if root is None else root
        before = self.snapshot(root)
        result = subprocess.run([sys.executable, "-B", str(Path(__file__).with_name("doctor")), str(root)],
                                capture_output=True, text=True, timeout=15)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(result.stderr, "")
        self.assertEqual(before, self.snapshot(root))
        self.assertIn("readiness: unproven", result.stdout)
        self.assertIn("commands: unverified defaults; no commands executed", result.stdout)
        return result.stdout

    def test_guidance_existing_gate_no_adapter_public(self):
        (self.root / "gate.py").write_text("COMMANDS = {'test': ['false']}\nraise AssertionError('never execute')\n")
        text = self.public_guidance()
        self.assertIn("verdict: 1 gap group(s).", text)
        self.assertNotIn("quality-gate/install", text)
        self.assertIn("Preserve existing gate.py", text)
        self.assertIn("explicit selections", text)
        self.assertIn("--preview-gate", text)
        self.assertIn("--apply-gate FINGERPRINT", text)
        self.assertIn("source shape is unverified", text)
        self.assertIn("Review remaining applicability, declarations and safety", text)
        self.assertIn("separate authority", text)

    def test_guidance_existing_gate_adapter_unresolved_public(self):
        (self.root / "gate.py").write_text("COMMANDS = {'test': ['false']}\n")
        (self.root / "package.json").write_text('{"scripts":{"bad":42,"good":"false"}}')
        web = self.root / "web"
        web.mkdir()
        (web / "package.json").write_text("{")
        (web / "vite.config.js").write_text("throw new Error('never execute');")
        (self.root / "Makefile").write_text("dev:\n\trm state.db\n")
        text = self.public_guidance()
        self.assertIn("verdict: 4 gap group(s).", text)
        self.assertIn("safe dev targets:          unsafe", text)
        self.assertIn('script name="good"; literal command="false"', text)
        self.assertIn("script value must be a string", text)
        self.assertIn("invalid JSON", text)
        self.assertNotIn("quality-gate/install", text)
        self.assertIn("Preserve existing gate.py", text)

    def test_guidance_makefile_complete_and_incomplete_public(self):
        (self.root / "pyproject.toml").write_text("# marker only\n")
        for complete in (True, False):
            with self.subTest(complete=complete):
                tasks = adopt.ORDER if complete else ["test"]
                (self.root / "Makefile").write_text("".join(task + ":\n\tfalse\n" for task in tasks))
                text = self.public_guidance()
                self.assertIn("verdict: %d gap group(s)." % (1 if complete else 6), text)
                self.assertIn("Makefile (complete)" if complete else "Makefile (missing targets:", text)
                self.assertNotIn("quality-gate/install", text)
                self.assertIn("Preserve existing Makefile", text)
                self.assertIn("native recipes", text)
                self.assertNotIn("--preview-gate", text)

    def test_guidance_missing_gate_adapter_public(self):
        (self.root / "pyproject.toml").write_text("# marker only\n")
        text = self.public_guidance()
        self.assertIn("verdict: 7 gap group(s).", text)
        self.assertIn("Optional scaffolding", text)
        line = next(line for line in text.splitlines() if line.startswith("Scaffolding command (JSON string; decode before use): "))
        command = json.loads(line.split(": ", 1)[1])
        self.assertEqual(shlex.split(command), ["python3", "quality-gate/install", str(self.root)])
        self.assertIn("requires Git and explicit write authority", text)
        self.assertIn("does not resolve all reported gaps", text)

    def test_guidance_missing_gate_no_adapter_public(self):
        text = self.public_guidance()
        self.assertIn("verdict: 7 gap group(s).", text)
        self.assertNotIn("quality-gate/install", text)
        self.assertIn("No adapter matched", text)
        self.assertIn("manual", text)
        self.assertIn("explicit selections", text)

    def test_guidance_commands_quote_and_escape_target_public(self):
        for name in ("space target", "quote'target", "line\n\x1btarget"):
            with self.subTest(name=name):
                root = self.root / name
                root.mkdir()
                (root / "pyproject.toml").write_text("# marker only\n")
                text = self.public_guidance(root)
                # Restrict inert-output assertion to new advice; legacy report rendering is unchanged.
                advice = text.split("verdict:", 1)[1]
                self.assertNotIn("\x1b", advice)
                lines = [line for line in advice.splitlines() if "command (JSON string; decode before use): " in line]
                self.assertEqual(len(lines), 2)
                for line in lines:
                    command = json.loads(line.split(": ", 1)[1])
                    args = shlex.split(command)
                    self.assertIn(str(root), args)
                    self.assertEqual(args[0], "python3")
                    self.assertNotIn("\n", line)

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


class ViteReadOwnership(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory(prefix="vite-ownership-")
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name).resolve()
        self.web = self.root / "web"
        self.web.mkdir()
        (self.web / "package.json").write_text('{"devDependencies":{"vitest":"*"}}')

    def test_real_config_reads_emit_no_resource_warning(self):
        (self.web / "vite.config.js").write_text("// envDir: false\nthrow new Error('inert');")
        gc.collect()
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always", ResourceWarning)
            facts = adopt.detect_vite(str(self.root))
            gc.collect()
        self.assertTrue(facts["env_isolated"])
        self.assertEqual([str(w.message) for w in caught if issubclass(w.category, ResourceWarning)], [])

    def test_config_handles_close_preserving_order_fields_and_shortcircuit(self):
        names = ["vite.config.z.js", "vite.config.directory", "vite.config.a.ts", "vite.config.tail.js"]
        (self.web / names[1]).mkdir()
        (self.web / "tsconfig.json").write_text("{}")
        real_open = open
        for match in (None, 0, 2):
            with self.subTest(match=match):
                for index in (0, 2, 3):
                    (self.web / names[index]).write_text("// envDir: false" if index == match else "malformed inert code")
                handles, opened = [], []

                def track(path, *args, **kwargs):
                    handle = real_open(path, *args, **kwargs)
                    handles.append(handle)
                    opened.append(Path(path).name)
                    return handle

                try:
                    with mock.patch.object(adopt.os, "listdir", return_value=names), \
                         mock.patch("builtins.open", side_effect=track):
                        facts = adopt.detect_vite(str(self.root))
                    self.assertEqual(facts, {"dir": "web", "vitest": True,
                        "configs": ["web/" + name for name in sorted(names)],
                        "env_isolated": match is not None, "typescript": True})
                    expected = [names[i] for i in (0, 2, 3) if match is None or i <= match]
                    self.assertEqual(opened, ["package.json", *expected])
                    self.assertTrue(all(handle.closed for handle in handles), opened)
                finally:
                    for handle in handles:
                        handle.close()

    def test_config_decode_error_propagates_and_closes_real_handle(self):
        config = self.web / "vite.config.js"
        config.write_bytes(b"\xff")
        real_open = open
        for strict in (True, False):
            with self.subTest(strict=strict):
                handles = []

                def track(path, *args, **kwargs):
                    handle = real_open(path, *args, **kwargs)
                    handles.append(handle)
                    return handle

                try:
                    with mock.patch("builtins.open", side_effect=track), self.assertRaises(UnicodeDecodeError):
                        adopt.detect_vite(str(self.root), strict_package_text=strict)
                    self.assertEqual(len(handles), 2)
                    self.assertTrue(all(handle.closed for handle in handles))
                finally:
                    for handle in handles:
                        handle.close()

    def test_config_open_error_is_not_swallowed(self):
        config = self.web / "vite.config.js"
        config.write_text("// envDir: false")
        real_open = open
        failure = PermissionError("synthetic unreadable config")

        def unreadable(path, *args, **kwargs):
            if Path(path) == config:
                raise failure
            return real_open(path, *args, **kwargs)

        with mock.patch("builtins.open", side_effect=unreadable), self.assertRaises(PermissionError) as raised:
            adopt.detect_vite(str(self.root))
        self.assertIs(raised.exception, failure)

    def test_absent_config_and_package_error_behavior(self):
        self.assertIsNone(adopt.detect_vite(str(self.root)))
        (self.web / "vite.config.js").write_text("// envDir: false")
        package = self.web / "package.json"
        package.write_text('{ malformed "vitest"')
        self.assertTrue(adopt.detect_vite(str(self.root))["vitest"])
        package.write_bytes(b"\xff")
        with self.assertRaises(UnicodeDecodeError):
            adopt.detect_vite(str(self.root))
        facts = adopt.detect_vite(str(self.root), strict_package_text=False)
        self.assertEqual((facts["dir"], facts["vitest"], facts["env_isolated"]), ("web", False, True))
        real_open = open

        def unreadable_package(path, *args, **kwargs):
            if Path(path) == package:
                raise PermissionError("synthetic unreadable package")
            return real_open(path, *args, **kwargs)

        with mock.patch("builtins.open", side_effect=unreadable_package):
            facts = adopt.detect_vite(str(self.root))
        self.assertEqual((facts["vitest"], facts["env_isolated"]), (False, True))


class ChildGoMarkers(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory(prefix="child-go-")
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name).resolve()

    def marker(self, directory, content=b"not parsed\xff"):
        child = self.root / directory
        child.mkdir(parents=True, exist_ok=True)
        (child / "go.mod").write_bytes(content)
        return child

    def evidence(self):
        # The helper may inspect directory metadata, never contents or executables.
        real_open = adopt.os.open

        def directory_only(path, flags, *args, **kwargs):
            self.assertTrue(flags & os.O_DIRECTORY)
            self.assertTrue(flags & os.O_NOFOLLOW)
            self.assertFalse(flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC))
            self.assertTrue(str(path) == str(self.root) or kwargs.get('dir_fd') is not None)
            return real_open(path, flags, *args, **kwargs)

        with mock.patch("builtins.open", side_effect=AssertionError("contents forbidden")), \
             mock.patch.object(adopt.os, "open", side_effect=directory_only), \
             mock.patch.object(adopt.subprocess, "run", side_effect=AssertionError("process forbidden")), \
             mock.patch.object(adopt, "_tool_version", side_effect=AssertionError("probe forbidden")), \
             mock.patch.object(adopt.os, "system", side_effect=AssertionError("shell forbidden")), \
             mock.patch.object(socket, "socket", side_effect=AssertionError("network forbidden")):
            return "\n".join(adopt.report_child_go_markers(str(self.root)))

    def candidate(self, directory):
        return 'working directory=%s; marker path=%s; unverified file presence' % (
            json.dumps(directory), json.dumps(directory + '/go.mod'))

    def test_child_go_mixed_audit_retains_frontend_and_gap_arithmetic(self):
        self.marker("backend")
        web = self.root / "frontend"
        web.mkdir()
        (web / "package.json").write_text('{"scripts":{"ui:check":"npm test"}}')
        (web / "vite.config.js").write_text('// envDir: false')
        (self.root / "package.json").write_text('{"scripts":{"root:check":"echo root"}}')
        (self.root / "gate.py").write_text("COMMANDS = {'test': ['old-check']}\n")
        (self.root / "Makefile").write_text('dev:\n\techo safe\n')
        (self.root / '.env').write_text('POISON=must-not-read')
        before = {str(p.relative_to(self.root)): (p.read_bytes(), p.stat().st_mode)
                  for p in self.root.rglob('*') if p.is_file()}
        real_open = open

        def declared_reads(path, mode='r', *args, **kwargs):
            self.assertNotIn(mode, ('w', 'a', 'x', 'r+'))
            self.assertIn(Path(path).relative_to(self.root).as_posix(), (
                'Makefile', 'package.json', 'frontend/package.json', 'frontend/vite.config.js'))
            return real_open(path, mode, *args, **kwargs)

        output = io.StringIO()
        with mock.patch.object(adopt.subprocess, "run", side_effect=AssertionError("process forbidden")), \
             mock.patch.object(adopt, "_tool_version", side_effect=AssertionError("probe forbidden")), \
             mock.patch('builtins.open', side_effect=declared_reads), \
             mock.patch.object(adopt.os, 'system', side_effect=AssertionError('shell forbidden')), \
             mock.patch.object(socket, 'socket', side_effect=AssertionError('network forbidden')), \
             contextlib.redirect_stdout(output):
            self.assertEqual(adopt.main(['adopt.py', 'audit', str(self.root)]), 0)
        self.assertEqual(before, {str(p.relative_to(self.root)): (p.read_bytes(), p.stat().st_mode)
                                 for p in self.root.rglob('*') if p.is_file()})
        text = output.getvalue()
        self.assertIn(self.candidate('backend'), text)
        self.assertIn('adapters matched:          bun', text)
        self.assertIn('script name="ui:check"; literal command="npm test"; working directory="frontend"', text)
        self.assertIn('script name="root:check"', text)
        self.assertIn('verdict: gate shape present.', text)
        self.assertIn('readiness: unproven', text)

    def test_child_go_root_only_absent_and_two_children_order(self):
        (self.root / 'go.mod').write_text('module root')
        (self.root / 'empty').mkdir()
        text = self.evidence()
        self.assertIn('no immediate-child candidates observed', text)
        self.assertNotIn('working directory="."', text)
        self.marker('z-backend')
        self.marker('a-backend', b'module synthetic/example\n')
        text = self.evidence()
        self.assertEqual(text, self.evidence())
        self.assertLess(text.index(self.candidate('a-backend')), text.index(self.candidate('z-backend')))
        self.assertEqual(text.count('; unverified file presence'), 2)

    def test_child_go_nonregular_and_linked_markers_are_uninspected(self):
        for name in ('directory', 'fifo', 'linked', 'outside-link'):
            (self.root / name).mkdir()
        (self.root / 'directory/go.mod').mkdir()
        os.mkfifo(self.root / 'fifo/go.mod')
        regular = self.marker('regular')
        (self.root / 'linked/go.mod').symlink_to(regular / 'go.mod')
        with tempfile.TemporaryDirectory(dir=self.root.parent) as outside:
            marker = Path(outside) / 'go.mod'
            marker.write_text('outside')
            (self.root / 'outside-link/go.mod').symlink_to(marker)
            (self.root / 'linked-child').symlink_to(outside, target_is_directory=True)
            text = self.evidence()
        self.assertEqual(text.count('; unverified file presence'), 1)
        for name in ('directory', 'fifo', 'linked', 'outside-link'):
            self.assertIn('marker path=%s; uninspected: linked or nonregular marker' % json.dumps(name + '/go.mod'), text)
        self.assertIn('working directory="linked-child"; uninspected: linked directory entry', text)

    def test_child_go_exclusions_and_deeper_scope(self):
        for name in ('.hidden', 'node_modules', 'vendor', 'dist', 'build', 'target', '__pycache__', 'venv'):
            self.marker(name)
        self.marker('services/api')
        real_open = adopt.os.open

        def scope_only(path, *args, **kwargs):
            self.assertIn(str(path), (str(self.root), 'services'))
            return real_open(path, *args, **kwargs)

        with mock.patch.object(adopt.os, 'open', side_effect=scope_only):
            text = self.evidence()
        self.assertNotIn('; unverified file presence', text)
        self.assertIn('deeper layouts uninspected', text)
        self.assertIn('hidden and dependency/build directories uninspected', text)
        self.assertNotIn('services/api/go.mod', text)

    def test_child_go_names_escaped_and_contents_inert(self):
        name = 'api space"\n\t\x1b café'
        self.marker(name, b'\xff\x00malformed\nmodule ???')
        text = self.evidence()
        self.assertIn(self.candidate(name), text)
        self.assertNotIn('\x1b', text)
        self.assertNotIn('café', text)
        self.assertNotIn('malformed', text)

    def test_child_go_enumeration_permission_error_is_unknown(self):
        with mock.patch.object(adopt.os, 'scandir', side_effect=PermissionError('private details')):
            text = self.evidence()
        self.assertIn('unknown/uninspected: cannot enumerate target', text)
        self.assertNotIn('no immediate-child candidates observed', text)
        self.assertNotIn('private details', text)

    def test_child_go_marker_permission_error_keeps_valid_sibling(self):
        self.marker('a-denied')
        self.marker('z-valid')
        real_stat = adopt.os.stat

        def denied(path, *args, **kwargs):
            if path == 'go.mod' and kwargs.get('dir_fd') is not None:
                directory = os.fstat(kwargs['dir_fd'])
                if directory.st_ino == (self.root / 'a-denied').stat().st_ino:
                    raise PermissionError('private details')
            return real_stat(path, *args, **kwargs)

        with mock.patch.object(adopt.os, 'stat', side_effect=denied):
            text = self.evidence()
        self.assertIn('working directory="a-denied"; marker path="a-denied/go.mod"; unknown/uninspected:', text)
        self.assertIn(self.candidate('z-valid'), text)
        self.assertNotIn('private details', text)

    def test_child_go_child_disappears_is_unknown(self):
        child = self.marker('backend')
        real_open = adopt.os.open

        def raced(path, *args, **kwargs):
            if path == 'backend':
                raise FileNotFoundError('synthetic race')
            return real_open(path, *args, **kwargs)

        with mock.patch.object(adopt.os, 'open', side_effect=raced):
            text = self.evidence()
        self.assertTrue(child.is_dir())
        self.assertIn('working directory="backend"; unknown/uninspected:', text)
        self.assertNotIn('no immediate-child candidates observed', text)

    def test_child_go_marker_disappears_is_unknown(self):
        self.marker('backend')
        real_stat = adopt.os.stat
        calls = 0

        def raced(path, *args, **kwargs):
            nonlocal calls
            if path == 'go.mod' and kwargs.get('dir_fd') is not None:
                calls += 1
                if calls == 2:
                    raise FileNotFoundError('synthetic race')
            return real_stat(path, *args, **kwargs)

        with mock.patch.object(adopt.os, 'stat', side_effect=raced):
            text = self.evidence()
        self.assertIn('marker path="backend/go.mod"; unknown/uninspected:', text)
        self.assertNotIn('; unverified file presence', text)

    def test_child_go_directory_replaced_by_outside_link_is_unknown(self):
        child = self.marker('backend')
        real_open = adopt.os.open
        with tempfile.TemporaryDirectory(dir=self.root.parent) as outside:
            (Path(outside) / 'go.mod').write_text('outside must never be inspected')

            def raced(path, *args, **kwargs):
                if path == 'backend':
                    child.rename(self.root / 'retained-backend')
                    child.symlink_to(outside, target_is_directory=True)
                return real_open(path, *args, **kwargs)

            with mock.patch.object(adopt.os, 'open', side_effect=raced):
                text = self.evidence()
        self.assertIn('working directory="backend"; unknown/uninspected:', text)
        self.assertNotIn('; unverified file presence', text)

    def test_child_go_marker_replaced_by_link_is_unknown_without_following(self):
        child = self.marker('backend')
        real_stat = adopt.os.stat
        calls = 0

        def raced(path, *args, **kwargs):
            nonlocal calls
            if path == 'go.mod' and kwargs.get('dir_fd') is not None:
                self.assertIs(kwargs.get('follow_symlinks'), False)
                calls += 1
                if calls == 2:
                    (child / 'go.mod').rename(child / 'retained-marker')
                    (child / 'go.mod').symlink_to(self.root / 'outside-nonexistent')
            return real_stat(path, *args, **kwargs)

        with mock.patch.object(adopt.os, 'stat', side_effect=raced):
            text = self.evidence()
        self.assertIn('marker path="backend/go.mod"; unknown/uninspected:', text)
        self.assertNotIn('; unverified file presence', text)

    def test_child_go_entry_metadata_error_is_unknown(self):
        entry = mock.Mock(name='entry')
        entry.name = 'backend'
        entry.stat.side_effect = PermissionError('private metadata')
        entries = mock.MagicMock()
        entries.__enter__.return_value = iter([entry])
        with mock.patch.object(adopt.os, 'scandir', return_value=entries):
            text = self.evidence()
        entry.stat.assert_called_once_with(follow_symlinks=False)
        self.assertIn('working directory="backend"; unknown/uninspected:', text)
        self.assertNotIn('no immediate-child candidates observed', text)
        self.assertNotIn('private metadata', text)

    def test_child_go_root_audit_preserves_old_output_and_never_uses_child_as_adapter(self):
        (self.root / 'go.mod').write_text('malformed inert root marker')
        output = io.StringIO()
        with mock.patch.object(adopt.subprocess, 'run', side_effect=AssertionError('process forbidden')), \
             contextlib.redirect_stdout(output):
            self.assertEqual(adopt.main(['adopt.py', 'audit', str(self.root)]), 0)
        text = output.getvalue()
        self.assertIn('adapters matched:          go', text)
        self.assertIn('go           marker=go.mod, version=unprobed', text)
        self.assertNotIn('working directory="."; marker path="go.mod"', text)
        self.assertIn('verdict: 7 gap group(s).', text)
        (self.root / 'go.mod').unlink()
        self.marker('backend')
        output = io.StringIO()
        with mock.patch.object(adopt.subprocess, 'run', side_effect=AssertionError('process forbidden')), \
             contextlib.redirect_stdout(output):
            self.assertEqual(adopt.main(['adopt.py', 'audit', str(self.root)]), 0)
        text = output.getvalue()
        self.assertIn('adapters matched:          none', text)
        self.assertIn('No adapter matched; use a manual native gate owner', text)
        self.assertIn(self.candidate('backend'), text)
        self.assertIn('verdict: 7 gap group(s).', text)


class ChildGoCapabilityContracts(unittest.TestCase):
    setUp = ChildGoMarkers.setUp
    marker = ChildGoMarkers.marker
    candidate = ChildGoMarkers.candidate

    def test_child_go_missing_flags_stop_before_filesystem_or_probes(self):
        self.marker('backend')
        for flag in ('O_RDONLY', 'O_DIRECTORY', 'O_NOFOLLOW', 'O_NONBLOCK'):
            with self.subTest(flag=flag), contextlib.ExitStack() as stack:
                stack.enter_context(mock.patch.dict(os.__dict__))
                del os.__dict__[flag]
                for name in ('open', 'scandir', 'stat', 'fstat', 'listdir', 'walk', 'system'):
                    stack.enter_context(mock.patch.object(os, name, side_effect=AssertionError('filesystem or shell forbidden')))
                stack.enter_context(mock.patch('builtins.open', side_effect=AssertionError('contents forbidden')))
                stack.enter_context(mock.patch.object(adopt.subprocess, 'run', side_effect=AssertionError('process forbidden')))
                stack.enter_context(mock.patch.object(adopt, '_tool_version', side_effect=AssertionError('probe forbidden')))
                stack.enter_context(mock.patch.object(socket, 'socket', side_effect=AssertionError('network forbidden')))
                text = '\n'.join(adopt.report_child_go_markers(str(self.root)))
                self.assertIn('unknown/uninspected: required no-follow directory inspection unavailable', text)
                self.assertNotIn('no immediate-child candidates observed', text)
                self.assertNotIn('; unverified file presence', text)
                self.assertNotIn('marker absent', text)

    def test_child_go_missing_flags_public_audit_preserves_root_gaps_and_exit(self):
        self.marker('backend')
        (self.root / 'go.mod').write_text('inert root marker')
        frontend = self.root / 'frontend'
        frontend.mkdir()
        (frontend / 'package.json').write_text('{"scripts":{"ui:check":"npm test"}}')
        (frontend / 'vite.config.js').write_text('// envDir: false')
        (self.root / '.env').write_text('POISON=must-not-read')
        real_open = open

        def declared_reads(path, mode='r', *args, **kwargs):
            self.assertEqual(mode, 'r')
            self.assertIn(Path(path).relative_to(self.root).as_posix(), (
                'Makefile', 'package.json', 'frontend/package.json', 'frontend/vite.config.js'))
            return real_open(path, mode, *args, **kwargs)

        for layout in ('root-gaps', 'mixed-gate', 'unresolved-script'):
            if layout == 'mixed-gate':
                (self.root / 'gate.py').write_text("COMMANDS = {'test': ['old-check']}\n")
                (self.root / 'Makefile').write_text('dev:\n\techo safe\n')
                (self.root / 'package.json').write_text('{"scripts":{"root:check":"echo root"}}')
            elif layout == 'unresolved-script':
                (self.root / 'package.json').write_text('{"scripts":{"bad":123}}')
            before = {str(p.relative_to(self.root)): (p.read_bytes(), p.stat().st_mode)
                      for p in self.root.rglob('*') if p.is_file()}
            baseline = io.StringIO()
            with mock.patch.object(adopt, 'report_child_go_markers', return_value=[]), \
                 contextlib.redirect_stdout(baseline):
                expected_code = adopt.main(['adopt.py', 'audit', str(self.root)])
            for flag in ('O_RDONLY', 'O_DIRECTORY', 'O_NOFOLLOW', 'O_NONBLOCK'):
                output, errors = io.StringIO(), io.StringIO()
                with self.subTest(layout=layout, flag=flag), contextlib.ExitStack() as stack:
                    stack.enter_context(mock.patch.dict(os.__dict__))
                    del os.__dict__[flag]
                    stack.enter_context(mock.patch.object(os, 'open', side_effect=AssertionError('directory open forbidden')))
                    stack.enter_context(mock.patch('builtins.open', side_effect=declared_reads))
                    stack.enter_context(mock.patch.object(adopt.subprocess, 'run', side_effect=AssertionError('process forbidden')))
                    stack.enter_context(mock.patch.object(adopt, '_tool_version', side_effect=AssertionError('probe forbidden')))
                    stack.enter_context(mock.patch.object(os, 'system', side_effect=AssertionError('shell forbidden')))
                    stack.enter_context(mock.patch.object(socket, 'socket', side_effect=AssertionError('network forbidden')))
                    stack.enter_context(contextlib.redirect_stdout(output))
                    stack.enter_context(contextlib.redirect_stderr(errors))
                    code = adopt.main(['adopt.py', 'audit', str(self.root)])
                    section = '\n'.join(adopt.report_child_go_markers(str(self.root))) + '\n'
                    self.assertIn('unknown/uninspected: required no-follow directory inspection unavailable', section)
                    self.assertEqual(output.getvalue().replace(section, '', 1), baseline.getvalue())
                    self.assertEqual((code, errors.getvalue()), (expected_code, ''))
                    self.assertEqual(code, 0)
                self.assertEqual(before, {str(p.relative_to(self.root)): (p.read_bytes(), p.stat().st_mode)
                                         for p in self.root.rglob('*') if p.is_file()})

    def test_child_go_unsupported_root_operations_are_unknown(self):
        self.marker('backend')
        for operation in ('open', 'scandir'):
            with self.subTest(operation=operation):
                with mock.patch.object(os, operation, side_effect=NotImplementedError('private capability details')):
                    text = '\n'.join(adopt.report_child_go_markers(str(self.root)))
                self.assertIn('unknown/uninspected: cannot enumerate target', text)
                self.assertNotIn('no immediate-child candidates observed', text)
                self.assertNotIn('private capability details', text)
                self.assertNotIn('; unverified file presence', text)

    def test_child_go_unsupported_child_and_marker_operations_keep_valid_sibling(self):
        child = self.marker('a-unsupported')
        self.marker('z-valid')
        child_inode = child.stat().st_ino
        real_open, real_stat, real_fstat = os.open, os.stat, os.fstat
        for operation in ('child-open', 'child-fstat', 'owner-stat', 'marker-stat', 'marker-recheck'):
            marker_calls = 0

            def open_directory(path, *args, **kwargs):
                if operation == 'child-open' and path == 'a-unsupported':
                    raise NotImplementedError('private capability details')
                return real_open(path, *args, **kwargs)

            def descriptor_stat(fd):
                metadata = real_fstat(fd)
                if operation == 'child-fstat' and metadata.st_ino == child_inode:
                    raise NotImplementedError('private capability details')
                return metadata

            def nofollow_stat(path, *args, **kwargs):
                nonlocal marker_calls
                if kwargs.get('dir_fd') is not None:
                    self.assertIs(kwargs.get('follow_symlinks'), False)
                    if path == 'a-unsupported' and operation == 'owner-stat':
                        raise NotImplementedError('private capability details')
                    if path == 'go.mod' and real_fstat(kwargs['dir_fd']).st_ino == child_inode:
                        marker_calls += 1
                        if operation == 'marker-stat' or (operation == 'marker-recheck' and marker_calls == 2):
                            raise NotImplementedError('private capability details')
                return real_stat(path, *args, **kwargs)

            with self.subTest(operation=operation):
                with mock.patch.object(os, 'open', side_effect=open_directory), \
                     mock.patch.object(os, 'fstat', side_effect=descriptor_stat), \
                     mock.patch.object(os, 'stat', side_effect=nofollow_stat):
                    text = '\n'.join(adopt.report_child_go_markers(str(self.root)))
                self.assertIn('working directory="a-unsupported";', text)
                self.assertIn('unknown/uninspected: metadata unavailable or changed', text)
                self.assertNotIn(self.candidate('a-unsupported'), text)
                self.assertIn(self.candidate('z-valid'), text)
                self.assertNotIn('marker absent', text)
                self.assertNotIn('private capability details', text)

    def test_child_go_unsupported_entry_nofollow_metadata_is_unknown(self):
        entry = mock.Mock()
        entry.name = 'backend'
        entry.stat.side_effect = NotImplementedError('private capability details')
        entries = mock.MagicMock()
        entries.__enter__.return_value = iter([entry])
        with mock.patch.object(os, 'scandir', return_value=entries):
            text = '\n'.join(adopt.report_child_go_markers(str(self.root)))
        entry.stat.assert_called_once_with(follow_symlinks=False)
        self.assertIn('working directory="backend"; unknown/uninspected:', text)
        self.assertNotIn('no immediate-child candidates observed', text)
        self.assertNotIn('private capability details', text)

    def test_child_go_programming_errors_are_not_hidden(self):
        self.marker('backend')
        for error in (AttributeError, TypeError):
            for operation in ('open', 'stat'):
                with self.subTest(error=error, operation=operation), \
                     mock.patch.object(os, operation, side_effect=error('synthetic programming bug')), \
                     self.assertRaisesRegex(error, 'synthetic programming bug'):
                    adopt.report_child_go_markers(str(self.root))



class PackageManagerEvidence(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory(prefix="manager-evidence-")
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name).resolve()

    def report(self, vite=None):
        before = {p.relative_to(self.root): (p.read_bytes(), p.stat().st_mode)
                  for p in self.root.rglob('*') if p.is_file()}
        real_open = open
        reads = []
        allowed = ['package.json'] + ([vite['dir'] + '/package.json'] if vite and vite['dir'] else [])

        def manifest_only(path, mode='r', *args, **kwargs):
            relative = Path(path).relative_to(self.root).as_posix()
            self.assertEqual(mode, 'r')
            self.assertIn(relative, allowed)
            reads.append(relative)
            return real_open(path, mode, *args, **kwargs)

        with mock.patch('builtins.open', side_effect=manifest_only), \
             mock.patch.object(adopt.subprocess, 'run', side_effect=AssertionError('process forbidden')), \
             mock.patch.object(adopt.subprocess, 'Popen', side_effect=AssertionError('process forbidden')), \
             mock.patch.object(adopt, '_tool_version', side_effect=AssertionError('probe forbidden')), \
             mock.patch.object(adopt.os, 'system', side_effect=AssertionError('shell forbidden')), \
             mock.patch.object(adopt.os, 'execve', side_effect=AssertionError('exec forbidden')), \
             mock.patch('builtins.exec', side_effect=AssertionError('exec forbidden')), \
             mock.patch.object(socket, 'socket', side_effect=AssertionError('network forbidden')):
            result = adopt.report_package_scripts(str(self.root), vite)
        self.assertEqual(reads, allowed)
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 2)
        self.assertEqual(before, {p.relative_to(self.root): (p.read_bytes(), p.stat().st_mode)
                                 for p in self.root.rglob('*') if p.is_file()})
        return '\n'.join(result[0]), result[1]

    def declaration(self, value, directory='.'):
        manifest = 'package.json' if directory == '.' else directory + '/package.json'
        return 'source manifest=%s; working directory=%s; packageManager=%s; declared/unverified' % (
            json.dumps(manifest), json.dumps(directory), json.dumps(value))

    def test_manager_public_doctor_observed_npm_field(self):
        path = self.root / 'package.json'
        path.write_text('{"packageManager":"npm@10.0.0","scripts":{"check":"node --test"}}')
        path.chmod(0o640)
        before = (path.read_bytes(), path.stat().st_mode)
        result = subprocess.run([sys.executable, '-B', str(Path(__file__).with_name('doctor')), str(self.root)],
                                capture_output=True, text=True, timeout=15)
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stderr, '')
        self.assertIn(self.declaration('npm@10.0.0'), result.stdout)
        self.assertIn('adapters matched:          bun', result.stdout)
        self.assertIn('package manager: unresolved', result.stdout)
        self.assertIn('script name="check"; literal command="node --test"', result.stdout)
        self.assertIn('readiness: unproven', result.stdout)
        self.assertEqual(before, (path.read_bytes(), path.stat().st_mode))

    def test_manager_distinct_root_vite_exact_values_and_scope(self):
        values = ('  npm@10.0.0+sha224.ABC  ', 'yarn@https://example.invalid/manager.js#sha224.ABC')
        (self.root / 'package.json').write_text(json.dumps({'packageManager': values[0]}))
        web = self.root / 'frontend'
        web.mkdir()
        (web / 'package.json').write_text(json.dumps({'packageManager': values[1]}))
        (self.root / '.env').write_text('DO_NOT_READ')
        (self.root / 'other').mkdir()
        (self.root / 'other/package.json').write_text('{"packageManager":"DO_NOT_DISCOVER"}')
        text, unresolved = self.report({'dir': 'frontend'})
        self.assertEqual(unresolved, 0)
        for value, directory in zip(values, ('.', 'frontend')):
            self.assertIn(self.declaration(value, directory), text)
        self.assertNotIn('DO_NOT_DISCOVER', text)
        self.assertIn('not format/pin/hash checked, installed, active or trusted; not an instruction', text)
        self.assertIn('legacy root adapters/scaffold defaults are not chosen from this declaration', text)
        self.assertEqual(text.count('; declared/unverified'), 2)
        text, unresolved = self.report({'dir': ''})
        self.assertEqual(text.count('; declared/unverified'), 1)

    def test_manager_absent_and_unusable_optional_no_extra_gaps(self):
        for package, status in [({}, 'packageManager absent; optional/informational')] + [
                ({'packageManager': value}, 'packageManager unusable optional declaration: ' + reason)
                for value, reason in [('', 'blank string'), (' \t\n', 'blank string'),
                                      (None, 'value must be a nonblank string'),
                                      (False, 'value must be a nonblank string'),
                                      (123, 'value must be a nonblank string'),
                                      (['DO_NOT_DUMP'], 'value must be a nonblank string'),
                                      ({'DO_NOT_DUMP': True}, 'value must be a nonblank string')]]:
            with self.subTest(package=package):
                package['scripts'] = {'bad': None, 'good': 'node --test'}
                (self.root / 'package.json').write_text(json.dumps(package))
                text, unresolved = self.report()
                prefix = 'manifest=' if 'packageManager' not in package else 'source manifest='
                self.assertIn(prefix + '"package.json"; working directory="."; ' + status, text)
                self.assertNotIn('DO_NOT_DUMP', text)
                self.assertNotIn('; declared/unverified', text)
                self.assertIn('script name="good"; literal command="node --test"', text)
                self.assertEqual(unresolved, 1)
                package['scripts'] = {'good': 'node --test'}
                (self.root / 'package.json').write_text(json.dumps(package))
                self.assertEqual(self.report()[1], 0)
        (self.root / 'package.json').write_text('{}')
        self.assertEqual(self.report()[1], 0)

    def test_manager_before_malformed_scripts_and_retained_other_manifest(self):
        web = self.root / 'frontend'
        web.mkdir()
        (web / 'package.json').write_text('{"packageManager":"pnpm@9","scripts":{"good":"check"}}')
        for scripts in (None, [], 'wrong', {'bad': False, 'good': 'retained'}):
            with self.subTest(scripts=scripts):
                (self.root / 'package.json').write_text(json.dumps({'packageManager': 'npm@10', 'scripts': scripts}))
                text, unresolved = self.report({'dir': 'frontend'})
                self.assertIn(self.declaration('npm@10'), text)
                self.assertLess(text.index(self.declaration('npm@10')), text.index('unresolved discovery:'))
                self.assertIn(self.declaration('pnpm@9', 'frontend'), text)
                self.assertIn('script name="good"; literal command="check"', text)
                if isinstance(scripts, dict):
                    self.assertIn('literal command="retained"', text)
                self.assertEqual(unresolved, 1)
        for raw, reason in (('{bad', 'invalid JSON'), ('[]', 'manifest must be an object'),
                            ('null', 'manifest must be an object')):
            with self.subTest(raw=raw):
                (self.root / 'package.json').write_text(raw)
                text, unresolved = self.report({'dir': 'frontend'})
                self.assertIn('unresolved discovery: ' + reason, text)
                self.assertIn(self.declaration('pnpm@9', 'frontend'), text)
                self.assertEqual(text.count('; declared/unverified'), 1)
                self.assertEqual(unresolved, 1)

    def test_manager_audit_same_reads_gaps_modes_no_execution(self):
        (self.root / '.env').write_text('NEVER_READ')
        (self.root / 'gate.py').write_text("COMMANDS = {'test': ['required-check']}\n")
        web = self.root / 'frontend'
        web.mkdir()
        (web / 'vite.config.js').write_text('// envDir: false')
        (web / 'package.json').write_text('{"packageManager":"pnpm@9","scripts":{"good":"check"}}')
        real_open = open
        observations = []
        for value in (None, '', False, [], {}, 'npm@10.0.0', 'https://example.invalid/never-fetch'):
            package = {'scripts': {'good': 'node --test', 'bad': False}}
            if value is not None:
                package['packageManager'] = value
            path = self.root / 'package.json'
            path.write_text(json.dumps(package))
            path.chmod(0o640)
            before = {p.relative_to(self.root): (p.read_bytes(), p.stat().st_mode)
                      for p in self.root.rglob('*') if p.is_file()}
            reads = []

            def audited_read(path, mode='r', *args, **kwargs):
                relative = Path(path).relative_to(self.root).as_posix()
                self.assertEqual(mode, 'r')
                self.assertIn(relative, ('package.json', 'frontend/package.json', 'frontend/vite.config.js'))
                reads.append(relative)
                return real_open(path, mode, *args, **kwargs)

            output = io.StringIO()
            with mock.patch('builtins.open', side_effect=audited_read), \
                 mock.patch.object(adopt.subprocess, 'run', side_effect=AssertionError('process forbidden')), \
                 mock.patch.object(adopt.subprocess, 'Popen', side_effect=AssertionError('process forbidden')), \
                 mock.patch.object(adopt, '_tool_version', side_effect=AssertionError('probe forbidden')), \
                 mock.patch.object(adopt.os, 'system', side_effect=AssertionError('shell forbidden')), \
                 mock.patch.object(adopt.os, 'execve', side_effect=AssertionError('exec forbidden')), \
                 mock.patch('builtins.exec', side_effect=AssertionError('exec forbidden')), \
                 mock.patch.object(socket, 'socket', side_effect=AssertionError('network forbidden')), \
                 contextlib.redirect_stdout(output):
                code = adopt.main(['adopt.py', 'audit', str(self.root)])
            text = output.getvalue()
            self.assertEqual(code, 0)
            self.assertIn('script name="good"; literal command="node --test"', text)
            self.assertIn(self.declaration('pnpm@9', 'frontend'), text)
            self.assertIn('script value must be a string', text)
            self.assertEqual(before, {p.relative_to(self.root): (p.read_bytes(), p.stat().st_mode)
                                     for p in self.root.rglob('*') if p.is_file()})
            observations.append((reads, [line for line in text.splitlines() if line.startswith('verdict:')]))
        self.assertTrue(all(observation == observations[0] for observation in observations))

    def test_manager_literal_quoted_controls_unicode_url_remain_inert(self):
        for value in ('npm@10.0.0', 'NPM@10.0.0+sha224.AbC',
                      'yarn@https://example.invalid/a.tgz#sha224.ABC',
                      'x";$(touch NEVER);`false`\nverdict: READY\r\t\x00\x1b[31m café\u202e'):
            with self.subTest(value=value):
                (self.root / 'package.json').write_text(json.dumps({'packageManager': value, 'scripts': {'good': 'check'}}))
                text, unresolved = self.report()
                self.assertIn(self.declaration(value), text)
                self.assertEqual(unresolved, 0)
                self.assertNotIn('\nverdict: READY', text)
                for control in ('\x00', '\x1b', '\r', '\t', 'é', '\u202e'):
                    self.assertNotIn(control, text)
                self.assertIn('literal command="check"', text)

if __name__ == "__main__":
    unittest.main()
