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

    def project_fixture(self):
        """Run the actual checker on a small complete source tree."""
        (self.manifests / "speckit.manifest.json").write_text('{"files": {}}')
        files = {
            "scripts/generate.py": "# Fixture generator has no outputs.\n",
            "scripts/source.py": "value = 1\n",
            "scripts/source.sh": "#!/usr/bin/env bash\ntrue\n",
            "bin/" + CHECK.core.SUITE: "#!/usr/bin/env bash\ntrue\n",
            ".githooks/pre-commit": "#!/usr/bin/env bash\ntrue\n",
            "README.md": "[Source](scripts/source.sh)\n",
            "site/index.html": "fixture\n",
            "site/style.css": "fixture\n",
            "site/app.js": "fixture\n",
            "site/diagrams/architecture.html": "fixture\n",
        }
        for relative, content in files.items():
            path = self.root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)

    def test_generated_nix_shells_are_not_project_shell_sources(self):
        self.project_fixture()
        for directory in (".devenv", ".devenv.instance", ".direnv"):
            path = self.root / directory / "shell-generated.sh"
            path.parent.mkdir()
            path.write_text("#!/usr/bin/env bash\nif then\n")
        CHECK.main()

    def test_generated_nix_python_and_links_are_not_project_sources(self):
        self.project_fixture()
        state = self.root / ".devenv"
        state.mkdir()
        (state / "generated.py").write_text("if then\n")
        (state / "generated.md").write_text("[Generated](missing-generated-file)\n")
        CHECK.main()

    def test_new_shell_sources_still_fail_real_shellcheck(self):
        self.project_fixture()
        for relative in ("scripts/new-source.sh", ".devcontainer/new-source.sh",
                         ".devenv.source.sh"):
            with self.subTest(relative=relative):
                path = self.root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("#!/usr/bin/env bash\nif then\n")
                real_run = CHECK.subprocess.run
                with patch.object(CHECK.subprocess, "run", side_effect=lambda *args, **kwargs:
                                  real_run(*args, capture_output=True, **kwargs)):
                    with self.assertRaises(CHECK.subprocess.CalledProcessError) as error:
                        CHECK.main()
                self.assertIn(str(path), error.exception.cmd)
                self.assertEqual(error.exception.cmd[0], "shellcheck")
                self.assertIn(b"SC107", error.exception.stdout + error.exception.stderr)
                path.unlink()

    def test_new_python_sources_still_fail_syntax_validation(self):
        self.project_fixture()
        (self.root / "scripts/new-source.py").write_text("if then\n")
        with self.assertRaises(SyntaxError):
            CHECK.main()

    def test_new_markdown_links_still_fail_validation(self):
        self.project_fixture()
        (self.root / "new-source.md").write_text("[Missing](missing-source-file)\n")
        with self.assertRaisesRegex(SystemExit, "new-source.md: broken link"):
            CHECK.main()
