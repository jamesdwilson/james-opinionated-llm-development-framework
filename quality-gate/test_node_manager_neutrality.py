"""Ordinary metadata ownership and explicit native adoption, without tool execution."""
import ast
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

SPEC = importlib.util.spec_from_file_location('adopt_node_neutrality', Path(__file__).with_name('adopt.py'))
adopt = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(adopt)
NATIVE = [('npm@10.9.0', 'package-lock.json', 'npm run check'),
          ('pnpm@9.15.0', 'pnpm-lock.yaml', 'pnpm run check'),
          ('yarn@4.6.0', 'yarn.lock', 'yarn run check')]


class NodeManagerNeutrality(unittest.TestCase):
    def setUp(self):
        fixture = tempfile.TemporaryDirectory(prefix='ordinary-node-')
        self.addCleanup(fixture.cleanup)
        self.root = Path(fixture.name).resolve()

    def project(self, name, declaration=None, locks=()):
        target = self.root / name
        target.mkdir()
        package = {'scripts': {'check': 'DO_NOT_EXECUTE'}}
        if declaration is not None:
            package['packageManager'] = declaration
        (target / 'package.json').write_text(json.dumps(package))
        for lock in locks:
            (target / lock).write_text('synthetic marker only\n')
        for path in target.iterdir():
            path.chmod(0o640)
        return target

    def snapshot(self, target):
        return {str(p.relative_to(target)): (p.read_bytes(), p.stat().st_mode & 0o7777)
                for p in target.rglob('*') if p.is_file()}

    def test_native_declarations_and_locks_never_select_or_probe_bun(self):
        for declaration, lock, _ in NATIVE:
            with self.subTest(manager=declaration):
                target = self.project(declaration, declaration, [lock])
                before = self.snapshot(target)
                with mock.patch.object(adopt, '_tool_version', side_effect=AssertionError('Bun probe forbidden')):
                    self.assertNotIn('bun', adopt.detect_all(str(target)))
                self.assertEqual(before, self.snapshot(target))

    def test_unspecified_and_declaration_only_ownership_stays_manual(self):
        for index, declaration in enumerate((None, 'npm@10.9.0', 'pnpm@9.15.0', 'yarn@4.6.0', 'bun@1.4.4')):
            with self.subTest(declaration=declaration):
                target = self.project(str(index), declaration)
                self.assertIsNone(adopt.detect_bun(str(target), probe_versions=False))

    def test_bun_lock_controls_retain_detection_and_optional_probe(self):
        for index, declaration in enumerate((None, 'bun@1.4.4')):
            target = self.project(str(index), declaration, ['bun.lock'])
            with mock.patch.object(adopt.shutil, 'which', return_value='/synthetic/bun'), \
                 mock.patch.object(adopt, '_tool_version', return_value='synthetic version') as probe:
                facts = adopt.detect_bun(str(target))
            self.assertEqual(facts, {'marker': 'bun.lock', 'lockfile': True, 'version': 'synthetic version'})
            probe.assert_called_once_with(['bun', '--version'])
        target = self.root / 'lock-only'
        target.mkdir()
        (target / 'bun.lock').write_text('synthetic marker')
        self.assertIsNotNone(adopt.detect_bun(str(target), probe_versions=False))

    def test_conflicting_lock_markers_stay_manual(self):
        for lock in ('package-lock.json', 'npm-shrinkwrap.json', 'pnpm-lock.yaml', 'yarn.lock'):
            with self.subTest(lock=lock):
                target = self.project(lock, 'bun@1.4.4', ['bun.lock', lock])
                self.assertIsNone(adopt.detect_bun(str(target), probe_versions=False))

    def test_bun_lock_with_conflicting_or_unusable_declaration_stays_manual(self):
        for index, declaration in enumerate(('npm@10.9.0', 'pnpm@9.15.0', 'yarn@4.6.0',
                                              'unknown@1', '', False, ['bun@1'])):
            with self.subTest(declaration=declaration):
                target = self.project(str(index), declaration, ['bun.lock'])
                self.assertIsNone(adopt.detect_bun(str(target), probe_versions=False))
        for index, raw in enumerate(('{', '[]', 'null')):
            target = self.project('malformed-' + str(index), locks=['bun.lock'])
            (target / 'package.json').write_text(raw)
            self.assertIsNone(adopt.detect_bun(str(target), probe_versions=False))

    def test_native_only_install_refuses_without_changing_existing_files(self):
        for declaration, lock, _ in NATIVE:
            target = self.project(declaration, declaration, [lock])
            (target / 'Makefile').write_text('test:\n\t@echo DO_NOT_EXECUTE\n')
            before = self.snapshot(target)
            output, errors = io.StringIO(), io.StringIO()
            with mock.patch.object(adopt.subprocess, 'run', return_value=subprocess.CompletedProcess([], 0)) as run, \
                 mock.patch.object(adopt, '_tool_version', side_effect=AssertionError('probe forbidden')), \
                 contextlib.redirect_stdout(output), contextlib.redirect_stderr(errors):
                code = adopt.main(['adopt.py', 'install', str(target)])
            self.assertEqual(code, 1)
            self.assertEqual(before, self.snapshot(target))
            self.assertEqual(run.call_args_list, [mock.call(
                ['git', '-C', str(target), 'rev-parse', '--is-inside-work-tree'], capture_output=True)])
            self.assertIn('explicit', errors.getvalue().lower())

    def test_mixed_python_native_frontend_gets_no_bun_scaffolding(self):
        target = self.project('mixed', 'npm@10.9.0', ['package-lock.json'])
        (target / 'requirements.txt').write_text('')
        (target / 'vite.config.js').write_text('throw new Error("DO_NOT_EXECUTE");')
        (target / 'playwright.config.ts').write_text('throw new Error("DO_NOT_EXECUTE");')
        package = json.loads((target / 'package.json').read_text())
        package['devDependencies'] = {'vitest': '*'}
        (target / 'package.json').write_text(json.dumps(package))
        before = self.snapshot(target)
        with mock.patch.object(adopt.subprocess, 'run', return_value=subprocess.CompletedProcess([], 0)), \
             mock.patch.object(adopt.shutil, 'which', return_value=None), \
             contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(adopt.main(['adopt.py', 'install', str(target)]), 0)
        for name, value in before.items():
            self.assertEqual(self.snapshot(target)[name], value)
        source = (target / 'gate.py').read_text()
        self.assertNotIn('bun ', source)
        self.assertIn('python3 -m pytest -q', source)
        self.assertFalse((target / 'env-isolation.test.ts').exists())
        first = self.snapshot(target)
        with mock.patch.object(adopt.subprocess, 'run', return_value=subprocess.CompletedProcess([], 0)), \
             mock.patch.object(adopt.shutil, 'which', return_value=None), \
             contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(adopt.main(['adopt.py', 'install', str(target)]), 0)
        self.assertEqual(first, self.snapshot(target))

    def test_bun_scaffolding_retains_root_defaults_and_nested_browser_config(self):
        target = self.project('bun', 'bun@1.4.4', ['bun.lock'])
        (target / 'vite.config.js').write_text('// envDir: false')
        (target / 'e2e').mkdir()
        (target / 'e2e/playwright.config.ts').write_text('throw new Error("DO_NOT_EXECUTE");')
        with mock.patch.object(adopt.subprocess, 'run', return_value=subprocess.CompletedProcess([], 0)), \
             mock.patch.object(adopt.shutil, 'which', return_value=None), \
             contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(adopt.main(['adopt.py', 'install', str(target)]), 0)
        source = (target / 'gate.py').read_text()
        self.assertIn('bun --no-env-file install --frozen-lockfile --ignore-scripts', source)
        self.assertIn('--cwd . vite build', source)
        self.assertIn('--cwd e2e playwright test', source)

    def test_root_bun_does_not_override_separate_native_frontend(self):
        target = self.project('mixed-bun', 'bun@1.4.4', ['bun.lock'])
        frontend = target / 'frontend'
        frontend.mkdir()
        (frontend / 'package.json').write_text('{"packageManager":"npm@10.9.0"}')
        (frontend / 'package-lock.json').write_text('synthetic marker')
        (frontend / 'vite.config.js').write_text('// envDir: false')
        (frontend / 'playwright.config.ts').write_text('throw new Error("DO_NOT_EXECUTE");')
        with mock.patch.object(adopt.subprocess, 'run', return_value=subprocess.CompletedProcess([], 0)), \
             mock.patch.object(adopt.shutil, 'which', return_value=None), \
             contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(adopt.main(['adopt.py', 'install', str(target)]), 0)
        source = (target / 'gate.py').read_text()
        self.assertIn('bun --no-env-file install', source)
        self.assertNotIn('--cwd frontend', source)

    def test_nested_browser_config_keeps_intervening_native_owner(self):
        for index, (declaration, lock, _) in enumerate(NATIVE + [('unknown@1', None, '')]):
            with self.subTest(manager=declaration):
                target = self.project('nested-' + str(index), 'bun@1.4.4', ['bun.lock'])
                frontend = target / 'frontend'
                (frontend / 'e2e').mkdir(parents=True)
                (frontend / 'package.json').write_text(json.dumps({
                    'packageManager': declaration,
                    'scripts': {'e2e': 'playwright test --config=e2e/playwright.config.ts'}}))
                if lock:
                    (frontend / lock).write_text('synthetic marker')
                (frontend / 'vite.config.js').write_text('// envDir: false')
                (frontend / 'e2e/playwright.config.ts').write_text('throw new Error("DO_NOT_EXECUTE");')
                before = self.snapshot(target)
                with mock.patch.object(adopt.subprocess, 'run', return_value=subprocess.CompletedProcess([], 0)), \
                     mock.patch.object(adopt.shutil, 'which', return_value=None), \
                     contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(adopt.main(['adopt.py', 'install', str(target)]), 0)
                source = (target / 'gate.py').read_text()
                self.assertIn('bun --no-env-file install', source)
                self.assertNotIn('--cwd frontend/e2e playwright', source)
                self.assertIn('requires an explicit native plan', (target / 'GATE.md').read_text())
                for name, original in before.items():
                    self.assertEqual(self.snapshot(target)[name], original)

    def cli(self, *args):
        return subprocess.run([sys.executable, '-B', *map(str, args)], capture_output=True, text=True, timeout=15)

    def test_public_doctor_and_explicit_native_plan_preview_apply_repeat(self):
        for declaration, lock, command in NATIVE + [('bun@1.4.4', 'bun.lock', 'bun run check')]:
            with self.subTest(manager=declaration):
                target = self.project(declaration, declaration, [lock])
                gate = target / 'gate.py'
                gate.write_text("from pathlib import Path\nPath(__file__).with_name('EXECUTED').touch()\n"
                                "COMMANDS = {'verify': ['policy-first'], 'test': ['owner-check']}\n")
                gate.chmod(0o640)
                before = self.snapshot(target)
                doctor = Path(__file__).with_name('doctor')
                first = self.cli(doctor, target)
                second = self.cli(doctor, target)
                self.assertEqual((first.returncode, first.stderr), (0, ''))
                self.assertEqual(first.stdout, second.stdout)
                expected = 'bun' if lock == 'bun.lock' else 'none'
                self.assertIn('adapters matched:          ' + expected, first.stdout)
                self.assertIn('declared/unverified', first.stdout)
                self.assertIn('readiness: unproven', first.stdout)
                args = [Path(__file__).with_name('adopt.py'), 'plan', target]
                selection = ['--command', 'test', '.', command]
                plan = self.cli(*args, *selection)
                self.assertEqual(plan.returncode, 0, plan.stderr)
                self.assertIn(command, plan.stdout)
                preview = self.cli(*args, '--preview-gate', *selection)
                self.assertEqual(preview.returncode, 0, preview.stderr)
                self.assertEqual(before, self.snapshot(target))
                fingerprint = preview.stdout.split('Confirmation SHA256: ')[1].splitlines()[0]
                applied = self.cli(*args, '--apply-gate', fingerprint, *selection)
                self.assertEqual(applied.returncode, 0, applied.stderr)
                tree = ast.parse(gate.read_bytes())
                value = next(n.value for n in tree.body if isinstance(n, ast.Assign))
                commands = ast.literal_eval(value)
                self.assertEqual(commands['verify'], ['policy-first'])
                self.assertEqual(commands['test'], ['owner-check', '(cd ./.' + ' && (\n' + command + '\n))'])
                self.assertEqual(gate.stat().st_mode & 0o7777, 0o640)
                for name, original in before.items():
                    if name != 'gate.py':
                        self.assertEqual(self.snapshot(target)[name], original)
                after = self.snapshot(target)
                again = self.cli(*args, '--preview-gate', *selection)
                fingerprint = again.stdout.split('Confirmation SHA256: ')[1].splitlines()[0]
                repeat = self.cli(*args, '--apply-gate', fingerprint, *selection)
                self.assertEqual(repeat.returncode, 0, repeat.stderr)
                self.assertIn('No changes to gate.py.', repeat.stdout)
                self.assertEqual(after, self.snapshot(target))
                self.assertFalse((target / 'EXECUTED').exists())


if __name__ == '__main__':
    unittest.main()
