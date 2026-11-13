import contextlib
import importlib.util
import io
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest import mock


_SPEC = importlib.util.spec_from_file_location(
    'adopt_scaffold_docs', Path(__file__).with_name('adopt.py')
)
adopt = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(adopt)


class ScaffoldDocumentationPreservationTests(unittest.TestCase):
    def setUp(self):
        self.fixture = tempfile.TemporaryDirectory(prefix='scaffold-docs-')
        self.addCleanup(self.fixture.cleanup)
        self.root = Path(self.fixture.name)
        self.target = self.root / 'target'
        self.target.mkdir()
        self.guide = self.target / 'GATE.md'
        requirements = self.target / 'requirements.txt'
        requirements.write_bytes(b'')
        requirements.chmod(0o640)
        gate = self.target / 'gate.py'
        gate.write_bytes(b'# Existing owner-controlled gate; never execute.\n')
        gate.chmod(0o640)
        self.original_files = {
            path: (path.read_bytes(), path.stat().st_mode & 0o7777)
            for path in (requirements, gate)
        }

    def _invoke_install(self):
        expected_git = [
            'git', '-C', str(self.target),
            'rev-parse', '--is-inside-work-tree',
        ]

        def admitted_git(command, *args, **kwargs):
            if command != expected_git:
                raise AssertionError(
                    'Unexpected subprocess request in bounded fixture: '
                    + repr(command)
                )
            return subprocess.CompletedProcess(command, 0, 'true', '')

        stdout = io.StringIO()
        stderr = io.StringIO()
        with mock.patch.object(
            adopt.shutil, 'which', return_value='/synthetic/tool'
        ), mock.patch.object(
            adopt, '_tool_version',
            return_value='Python 3.12.0 (synthetic fixture version)',
        ), mock.patch.object(
            adopt.subprocess, 'run', side_effect=admitted_git
        ), contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            try:
                result = adopt.main(['adopt.py', 'install', str(self.target)])
            except OSError as error:
                self.fail(
                    'Scaffolding attempted an incompatible filesystem operation '
                    'on an existing entry instead of preserving it: '
                    + repr(error)
                )
        self.assertEqual(result, 0, 'Preservation must permit normal scaffolding')
        for path, (contents, mode) in self.original_files.items():
            self.assertEqual(path.read_bytes(), contents, str(path))
            self.assertEqual(path.stat().st_mode & 0o7777, mode, str(path))
        return stdout.getvalue() + '\n' + stderr.getvalue()

    def _assert_preservation_report(self, output):
        guide_lines = '\n'.join(
            line for line in output.splitlines() if 'gate.md' in line.lower()
        )
        self.assertTrue(guide_lines, 'Report must identify existing GATE.md')
        self.assertRegex(
            guide_lines.lower(),
            r'\b(preserv\w*|kept|retain\w*|leav\w*|unchanged|untouched|skip\w*|already exists)\b',
            'Report must communicate that existing guidance was preserved',
        )
        self.assertNotRegex(
            guide_lines.lower(),
            r'\b(wrote|written|created|generated|overwrote)\s+[`\'"]?gate\.md\b',
            'Report must not claim it wrote the preserved guide',
        )
        self.assertNotRegex(
            guide_lines.lower(),
            r'\bgate\.md[`\'"]?\s+(?:was\s+|has been\s+)?(written|created|generated|overwritten)\b',
            'Report must not claim the preserved guide was written',
        )

    def _assert_regular_guide(self, contents, mode):
        self.assertFalse(self.guide.is_symlink())
        self.assertTrue(self.guide.is_file())
        self.assertEqual(
            self.guide.read_bytes(), contents,
            'Existing user guidance bytes must survive scaffolding',
        )
        self.assertEqual(self.guide.stat().st_mode & 0o7777, mode)

    def _link_identity(self):
        metadata = self.guide.lstat()
        return (
            os.readlink(self.guide), metadata.st_dev,
            metadata.st_ino, metadata.st_mode,
        )

    def test_existing_regular_guide_preserves_arbitrary_bytes_and_mode(self):
        contents = b'Owner instructions\n\x00\xff\n' + 'Keep café guidance.\n'.encode('utf-8')
        self.guide.write_bytes(contents)
        self.guide.chmod(0o640)

        output = self._invoke_install()

        self._assert_regular_guide(contents, 0o640)
        self._assert_preservation_report(output)

    def test_reinstall_preserves_explicit_user_edits_to_generated_guide(self):
        self._invoke_install()
        self.assertTrue(self.guide.is_file())
        generated = self.guide.read_bytes()
        self.assertTrue(generated.strip())
        edited = generated + b'\nUSER-OWNED INSTRUCTIONS: retain this exact addition.\n'
        self.guide.write_bytes(edited)
        self.guide.chmod(0o600)

        output = self._invoke_install()

        self._assert_regular_guide(edited, 0o600)
        self._assert_preservation_report(output)

    def test_existing_symlink_preserves_link_and_owned_external_file(self):
        destination = self.root / 'owned-external-guide.md'
        contents = b'External owner instructions\n\xff\n'
        destination.write_bytes(contents)
        destination.chmod(0o640)
        self.guide.symlink_to(destination)
        identity = self._link_identity()

        output = self._invoke_install()

        self.assertEqual(
            destination.read_bytes(), contents,
            'Scaffolding must not follow GATE.md to overwrite the owned external canary',
        )
        self.assertEqual(destination.stat().st_mode & 0o7777, 0o640)
        self.assertTrue(self.guide.is_symlink())
        self.assertEqual(self._link_identity(), identity)
        self._assert_preservation_report(output)

    def test_dangling_symlink_preserves_link_without_creating_destination(self):
        destination = self.root / 'owned-not-yet-existing-guide.md'
        self.assertFalse(os.path.lexists(destination))
        self.guide.symlink_to(destination)
        identity = self._link_identity()

        output = self._invoke_install()

        self.assertFalse(
            os.path.lexists(destination),
            'Scaffolding must not follow a dangling GATE.md link to create a file',
        )
        self.assertTrue(self.guide.is_symlink())
        self.assertEqual(self._link_identity(), identity)
        self._assert_preservation_report(output)

    def test_existing_directory_preserves_entry_contents_and_mode(self):
        self.guide.mkdir()
        child = self.guide / 'owner-instructions.bin'
        contents = b'Directory-owned instructions\n\x00\xff'
        child.write_bytes(contents)
        child.chmod(0o640)
        self.guide.chmod(0o750)
        metadata = self.guide.stat()
        identity = (metadata.st_dev, metadata.st_ino)

        output = self._invoke_install()

        self.assertFalse(self.guide.is_symlink())
        self.assertTrue(self.guide.is_dir())
        metadata = self.guide.stat()
        self.assertEqual((metadata.st_dev, metadata.st_ino), identity)
        self.assertEqual(metadata.st_mode & 0o7777, 0o750)
        self.assertEqual(set(self.guide.iterdir()), {child})
        self.assertEqual(child.read_bytes(), contents)
        self.assertEqual(child.stat().st_mode & 0o7777, 0o640)
        self._assert_preservation_report(output)

    def test_missing_guide_receives_meaningful_generated_guidance(self):
        self.assertFalse(os.path.lexists(self.guide))

        self._invoke_install()

        self.assertFalse(self.guide.is_symlink())
        self.assertTrue(self.guide.is_file())
        guidance = self.guide.read_text(encoding='utf-8')
        self.assertGreater(len(guidance.strip()), 80)
        self.assertIn('gate.py', guidance)


if __name__ == '__main__':
    unittest.main()
