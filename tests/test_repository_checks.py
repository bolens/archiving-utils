"""Regression coverage for the managed-file validation boundary."""
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

SPEC = importlib.util.spec_from_file_location(
    "repository_check", Path(__file__).resolve().parents[1] / "scripts/check.py"
)
CHECK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK)


class ManagedChecks(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.patch = patch.object(CHECK, "ROOT", self.root)
        self.patch.start()
        self.addCleanup(self.patch.stop)
        self.manifests = self.root / ".specify/integrations"
        self.manifests.mkdir(parents=True)
        (self.manifests / "codex.manifest.json").write_text('{"files": {}}')

    def manifest(self, relative, content):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        (self.manifests / "speckit.manifest.json").write_text(
            json.dumps({"files": {relative: digest}})
        )
        return path

    def test_verified_script_uses_bash_syntax_without_project_style_rules(self):
        path = self.manifest(".specify/scripts/bash/common.sh", "echo '$literal'\n")
        self.assertEqual(CHECK.managed_spec_kit_files(), {path})

    def test_changed_managed_file_fails(self):
        path = self.manifest(".specify/scripts/bash/common.sh", "true\n")
        path.write_text("false\n")
        with self.assertRaisesRegex(SystemExit, "hash mismatch"):
            CHECK.managed_spec_kit_files()

    def test_owned_file_cannot_be_exempted(self):
        self.manifest("README.md", "[broken](missing.md)\n")
        self.assertEqual(CHECK.managed_spec_kit_files(), set())

    def test_missing_manifest_fails(self):
        with self.assertRaisesRegex(SystemExit, "missing.*manifest"):
            CHECK.managed_spec_kit_files()

    def test_invalid_bash_fails_even_with_matching_hash(self):
        import subprocess
        self.manifest(".specify/scripts/bash/common.sh", "if then\n")
        with self.assertRaises(subprocess.CalledProcessError):
            CHECK.managed_spec_kit_files()

    def test_parent_symlink_cannot_escape_repository(self):
        path = self.manifest(".specify/scripts/bash/common.sh", "true\n")
        with tempfile.TemporaryDirectory() as outside:
            (Path(outside) / "common.sh").write_text("true\n")
            path.unlink()
            path.parent.rmdir()
            path.parent.symlink_to(outside, target_is_directory=True)
            with self.assertRaisesRegex(SystemExit, "missing or symlinked"):
                CHECK.managed_spec_kit_files()

    def test_parent_traversal_is_rejected_before_reading(self):
        (self.manifests / "speckit.manifest.json").write_text(
            json.dumps({"files": {"../outside": "0" * 64}})
        )
        with self.assertRaisesRegex(SystemExit, "unsafe.*path"):
            CHECK.managed_spec_kit_files()
