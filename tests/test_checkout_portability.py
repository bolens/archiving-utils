"""Run the real CLI and developer commands from a renamed disposable checkout."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SUITE = "archiving-utils"


class CheckoutPortability(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.temp.cleanup)
        base = Path(cls.temp.name)
        cls.checkout = base / "renamed checkout 雪"
        cls.checkout.mkdir()
        tracked = subprocess.run(
            ["git", "ls-files", "-z"], cwd=ROOT, check=True, capture_output=True
        ).stdout
        for entry in tracked.split(b"\0"):
            if not entry:
                continue
            relative = Path(os.fsdecode(entry))
            target = cls.checkout / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / relative, target, follow_symlinks=False)
        cls.env = os.environ.copy()
        for variable, directory in {
            "HOME": "home", "XDG_CONFIG_HOME": "config", "XDG_CACHE_HOME": "cache",
            "XDG_DATA_HOME": "data", "TMPDIR": "tmp",
        }.items():
            path = base / directory
            path.mkdir()
            cls.env[variable] = str(path)

    def command(self, *args):
        return subprocess.run(
            args, cwd=self.checkout, env=self.env, capture_output=True,
            text=True, timeout=60, check=False,
        )

    def assert_success(self, result):
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_native_checks_and_generated_files_survive_rename(self):
        self.assert_success(self.command("make", "check"))

    def test_help_keeps_the_suite_name(self):
        result = self.command("bin/" + SUITE, "--help")
        self.assert_success(result)
        self.assertIn("Usage: bin/" + SUITE + " TOOL", result.stdout)
        result = self.command("make", "help")
        self.assert_success(result)
        self.assertIn("bin/" + SUITE + " TOOL --help", result.stdout)

    def test_per_tool_make_works_in_path_with_spaces(self):
        self.assert_success(self.command("make", "-C", "util/library/library-inventory", "help"))

    def test_default_config_namespace_stays_stable(self):
        data = Path(self.temp.name) / "fixture-input"
        data.mkdir()
        source = data / "fixture.txt"
        source.write_text("preserve this fixture")
        config = Path(self.env["XDG_CONFIG_HOME"]) / SUITE
        config.mkdir()
        (config / "config.json").write_text(json.dumps({"roots": [str(data)]}))
        result = self.command("bin/" + SUITE, "library-inventory")
        self.assert_success(result)
        self.assertIn("fixture.txt", result.stdout)
        self.assertEqual(source.read_text(), "preserve this fixture")
