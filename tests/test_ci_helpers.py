"""Exercise the compatibility entrypoint with isolated executable boundaries."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
BACKEND = "bsdtar"


class PythonLane(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="utility-ci-test-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.checkout = self.root / "checkout with spaces"
        self.bin = self.root / "bin"
        self.bin.mkdir()
        self.scratch = self.root / "scratch"
        self.scratch.mkdir()
        target = self.checkout / "scripts/ci/check-python.sh"
        target.parent.mkdir(parents=True)
        shutil.copy2(ROOT / "scripts/ci/check-python.sh", target)
        self.script = target
        for name in ["dirname", "mktemp", "mkdir", "rm", "env", "tee"]:
            (self.bin / name).symlink_to(shutil.which(name))
        self.executable("python3", '''import os,sys
if sys.argv[1:]==["--version"]:
 print("Python "+os.environ["FIXTURE_PYTHON"])
elif "find_library" in sys.argv[2]:
 sys.exit(int(os.environ.get("BACKEND_EXIT", "0")))
else:
 print(os.environ["FIXTURE_PYTHON"])
''')
        self.executable("make", '''import os,sys,json
from pathlib import Path
names=["HOME","XDG_CONFIG_HOME","XDG_CACHE_HOME","XDG_STATE_HOME","XDG_DATA_HOME","XDG_RUNTIME_DIR","TMPDIR"]
assert all(Path(os.environ[name]).is_dir() for name in names)
Path(os.environ["MAKE_RECORD"]).write_text(json.dumps({"args":sys.argv[1:],"environment":{name:os.environ[name] for name in names}}))
print("make output is preserved")
sys.exit(int(os.environ.get("MAKE_EXIT", "0")))
''')
        for name in ["ffmpeg", "ffprobe", "bsdtar", "magick"]:
            self.executable(name, 'print("real backend boundary fixture")\n')
        self.record = self.root / "make.json"
        self.environment = {
            "PATH": str(self.bin), "TMPDIR": str(self.scratch),
            "FIXTURE_PYTHON": "3.11", "MAKE_RECORD": str(self.record),
            "LANG": "C.UTF-8", "LC_ALL": "C.UTF-8",
        }

    def executable(self, name, text):
        path = self.bin / name
        path.write_text("#!" + sys.executable + "\n" + text)
        path.chmod(0o700)

    def run_lane(self, *arguments, **changes):
        environment = dict(self.environment, **changes)
        result = subprocess.run(
            [shutil.which("bash"), str(self.script), *arguments],
            cwd=self.root, env=environment, capture_output=True, text=True, timeout=15,
        )
        self.assertEqual(list(self.scratch.iterdir()), [], "Owned scratch leaked")
        return result

    def test_both_supported_lanes_use_canonical_make_and_private_environment(self):
        for version in ["3.11", "3.14"]:
            with self.subTest(version=version):
                result = self.run_lane(version, FIXTURE_PYTHON=version)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                recorded = json.loads(self.record.read_text())
                self.assertEqual(recorded["args"], ["PYTHON=python3", "check", "test-all"])
                for path in recorded["environment"].values():
                    self.assertTrue(Path(path).is_relative_to(self.scratch))
                    self.assertFalse(Path(path).exists())
                self.assertIn("make output is preserved", result.stdout)

    def test_wrong_interpreter_fails_before_backend_or_make(self):
        result = self.run_lane("3.11", FIXTURE_PYTHON="3.14")
        self.assertEqual(result.returncode, 2)
        self.assertIn("Expected Python 3.11, found 3.14", result.stderr)
        self.assertFalse(self.record.exists())

    def test_missing_required_backend_fails_instead_of_skipping_tests(self):
        (self.bin / BACKEND).unlink()
        result = self.run_lane("3.11")
        self.assertEqual(result.returncode, 2)
        self.assertIn("backend missing", result.stderr)
        self.assertFalse(self.record.exists())

    def test_make_failure_survives_tee_and_removes_owned_environment(self):
        result = self.run_lane("3.11", MAKE_EXIT="53")
        self.assertEqual(result.returncode, 53)
        self.assertIn("make output is preserved", result.stdout)
        self.assertTrue(self.record.exists())

    def test_unsupported_lane_or_missing_argument_is_usage_error(self):
        for arguments in [(), ("3.15",), ("3.11", "unexpected")]:
            with self.subTest(arguments=arguments):
                self.assertEqual(self.run_lane(*arguments).returncode, 2)
                self.assertFalse(self.record.exists())

    def test_missing_libarchive_shared_library_fails_before_make(self):
        result = self.run_lane("3.11", BACKEND_EXIT="1")
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(self.record.exists())


if __name__ == "__main__":
    unittest.main()
