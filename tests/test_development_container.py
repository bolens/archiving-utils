"""CLI contracts for local development image adapters."""
import importlib.util
import json
import re
import subprocess
import tempfile
from fnmatch import fnmatchcase
import unittest
from pathlib import Path
from unittest.mock import patch

SPEC = importlib.util.spec_from_file_location("development_container", Path(__file__).resolve().parents[1] / "scripts" / "development-container.py")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class DevelopmentContainerTests(unittest.TestCase):
    def test_preserves_command_arguments_and_checkout_spaces(self):
        for engine in ("docker", "podman", "apple"):
            with self.subTest(engine=engine):
                args = ["python3", "-c", "print('$HOME; a b')"]
                cmd = MODULE.command(engine, "run", Path("/tmp/repo with spaces"), args)
                self.assertEqual(cmd[-3:], args)
                self.assertIn("type=bind,source=/tmp/repo with spaces,target=/workspace", cmd)
                self.assertNotIn("--tty", cmd)

    def test_podman_preserves_user_mapping(self):
        self.assertIn("--userns=keep-id", MODULE.command("podman", "run", Path("/tmp/repo")))
        self.assertNotIn("--userns=keep-id", MODULE.command("docker", "run", Path("/tmp/repo")))

    def test_engine_archive_loading(self):
        for engine in ("docker", "podman", "apple"):
            cmd = MODULE.command(engine, "load", Path("/tmp/repo"))
            self.assertEqual(cmd[0], "container" if engine == "apple" else engine)
            self.assertEqual(cmd[1:4], ["image", "load", "--input"])

    @patch.object(MODULE.shutil, "which", return_value="/fixture/docker")
    @patch.object(MODULE.subprocess, "run")
    def test_child_failure_is_returned(self, run, _which):
        run.return_value.returncode = 19
        self.assertEqual(MODULE.main(["run", "docker", "--", "false"]), 19)

    @patch.object(MODULE.shutil, "which", return_value=None)
    def test_missing_engine_fails_before_running(self, _which):
        with self.assertRaises(SystemExit) as result:
            MODULE.main(["run", "docker"])
        self.assertEqual(result.exception.code, 2)


class DevelopmentWorkflowTests(unittest.TestCase):
    """Exercise the selected workflow shell using only recording executables."""

    def workflow(self):
        return (Path(__file__).resolve().parents[1] / ".github/workflows/devenv.yml").read_text()

    def smoke_script(self):
        source = self.workflow()
        start = source.index("      - name: Validate VS Code devcontainer image\n")
        step = source[start:source.index("\n  result:", start)]
        self.assertIn("        if: runner.os == 'Linux'\n", step)
        script = step.split("        run: |\n", 1)[1]
        return "\n".join(line[10:] for line in script.splitlines()) + "\n"

    def test_devcontainer_changes_select_environment_and_existing_nix_proof_stays(self):
        source = self.workflow()
        block = source.split("            environment:\n", 1)[1].split("\n\n", 1)[0]
        patterns = re.findall(r"^              - '([^']+)'$", block, re.M)
        self.assertEqual(patterns.count('.devcontainer/**'), 1)
        for path in ('.devcontainer/Dockerfile', '.devcontainer/devcontainer.json',
                     '.devcontainer/post-create.sh', '.devcontainer/smoke.sh',
                     '.devcontainer/.dockerignore', '.devcontainer/nested/helper.sh'):
            self.assertTrue(any(fnmatchcase(path, item) for item in patterns), path)
        self.assertFalse(any(fnmatchcase('unselected.tmp', item) for item in patterns))
        self.assertIn('python3 scripts/development-container.py build docker', source)
        self.assertIn('python3 scripts/development-container.py run docker -- make check test-all', source)
        config = json.loads((Path(__file__).resolve().parents[1] / '.devcontainer/devcontainer.json').read_text())
        self.assertEqual(config['build'], {'dockerfile': 'Dockerfile', 'context': '.'})
        self.assertEqual(config['workspaceFolder'], '/workspace')
        self.assertEqual(config['remoteUser'], 'vscode')
        self.assertTrue(config['updateRemoteUserUID'])
        self.assertEqual(config['postCreateCommand'], ['bash', '.devcontainer/post-create.sh'])

    def record(self, *, uid='1001', build_exit='0'):
        with tempfile.TemporaryDirectory(prefix='devcontainer workflow ') as directory:
            root = Path(directory).resolve()
            binary = root / 'bin'
            binary.mkdir()
            trace = root / 'docker.jsonl'
            identity = binary / 'id'
            identity.write_text('#!/bin/sh\ncase "$1" in -u) printf "%s\\n" "$TEST_UID";; -g) printf "1001\\n";; *) exit 91;; esac\n')
            identity.chmod(0o755)
            docker = binary / 'docker'
            docker.write_text('#!/usr/bin/python3\nimport json,os,sys\nwith open(os.environ["TRACE"],"a") as stream:stream.write(json.dumps(sys.argv[1:])+"\\n")\nif sys.argv[1]=="build":sys.exit(int(os.environ["BUILD_EXIT"]))\n')
            docker.chmod(0o755)
            script = root / 'workflow.sh'
            script.write_text(self.smoke_script())
            result = subprocess.run(['bash', str(script)], cwd=root, capture_output=True,
                                    env={'PATH': str(binary) + ':/usr/bin:/bin', 'HOME': str(root),
                                         'TRACE': str(trace), 'TEST_UID': uid, 'BUILD_EXIT': build_exit},
                                    timeout=10)
            calls = [json.loads(line) for line in trace.read_text().splitlines()] if trace.exists() else []
            return result.returncode, calls, str(root)

    def test_real_devcontainer_context_and_smoke_are_nonroot_without_host_socket(self):
        status, calls, root = self.record()
        self.assertEqual(status, 0)
        self.assertEqual(len(calls), 2)
        self.assertEqual(calls[0], ['build', '--pull', '--tag', 'archiving-utils-devcontainer:ci', '.devcontainer'])
        run = calls[1]
        self.assertEqual(run[:4], ['run', '--rm', '--network=none', '--read-only'])
        self.assertIn('--cap-drop=ALL', run)
        self.assertIn('--security-opt=no-new-privileges', run)
        self.assertEqual(run[run.index('--user') + 1], '1001:1001')
        self.assertEqual(run[run.index('--mount') + 1], f'type=bind,source={root},target=/workspace')
        self.assertEqual(run.count('--mount'), 1)
        self.assertNotIn('/var/run/docker.sock', ' '.join(run))
        self.assertIn('HOME=/tmp', run)
        self.assertEqual(run[-5:], ['--workdir', '/workspace', 'archiving-utils-devcontainer:ci', 'bash', '.devcontainer/post-create.sh'])

    def test_symlinked_temporary_parent_matches_physical_shell_workdir(self):
        with tempfile.TemporaryDirectory() as directory:
            parent = Path(directory).resolve()
            physical = parent / 'physical temporary parent'
            physical.mkdir()
            alias = parent / 'temporary alias'
            alias.symlink_to(physical, target_is_directory=True)
            with patch.object(tempfile, 'tempdir', str(alias)):
                status, calls, root = self.record()
            self.assertEqual(status, 0)
            self.assertEqual(len(calls), 2)
            self.assertEqual(Path(root).parent, physical)
            run = calls[1]
            self.assertEqual(run[run.index('--mount') + 1], f'type=bind,source={root},target=/workspace')
            self.assertNotIn(str(alias), ' '.join(run))

    def test_root_or_failed_build_cannot_reach_smoke(self):
        status, calls, _ = self.record(uid='0')
        self.assertNotEqual(status, 0)
        self.assertEqual(calls, [])
        status, calls, _ = self.record(build_exit='19')
        self.assertEqual(status, 19)
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0][0], 'build')


if __name__ == "__main__":
    unittest.main()
