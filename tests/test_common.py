"""Shared behavior tests using only isolated disposable trees."""

import json
import concurrent.futures
from unittest import mock
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "lib"))
import core


class Fixture(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="utility-test-")
        self.addCleanup(self.temp.cleanup)
        self.work = Path(self.temp.name)
        self.home = self.work / "home"
        self.home.mkdir()
        self.inputs = self.work / "inputs"
        self.inputs.mkdir()
        self.env = dict(
            os.environ,
            HOME=str(self.home),
            XDG_CONFIG_HOME=str(self.home / "config"),
            XDG_STATE_HOME=str(self.home / "state"),
            TMPDIR=str(self.work),
        )

    def cli(self, *args, code=0):
        result = subprocess.run(
            [sys.executable, str(ROOT / "lib/core.py"), *map(str, args)],
            env=self.env,
            capture_output=True,
            text=True,
            timeout=120,
        )
        self.assertEqual(result.returncode, code, result.stderr + "\n" + result.stdout)
        return result

    def file(self, name="sample.bin", data=b"fixture data"):
        path = self.inputs / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        return path


class Common(Fixture):
    def test_help_every_tool(self):
        for tool in core.catalog():
            with self.subTest(tool=tool["name"]):
                self.cli(tool["name"], "--help")

    def test_wrappers(self):
        for path in sorted(ROOT.glob("**/*.sh")):
            if "conversion" in path.parts or "util" in path.parts:
                r = subprocess.run(
                    ["bash", str(path), "--help"], capture_output=True, env=self.env
                )
                self.assertEqual(r.returncode, 0, str(path))

    def test_inventory_hostile_names(self):
        names = [
            "a space.bin",
            "-dash.bin",
            "[brackets]*?.bin",
            "unicodé.bin",
            "line\nbreak.bin",
            "$(touch SHOULD_NOT_EXIST).bin",
        ]
        for name in names:
            self.file(name)
        result = json.loads(self.cli("library-inventory", self.inputs).stdout)
        self.assertEqual({row["relative"] for row in result["results"]}, set(names))
        self.assertFalse((self.work / "SHOULD_NOT_EXIST").exists())

    def test_duplicates(self):
        self.file("one")
        self.file("two")
        self.file("three", b"different")
        rows = json.loads(self.cli("library-dupes", self.inputs).stdout)["results"]
        self.assertEqual(len(rows), 1)
        self.assertEqual(len(rows[0]["paths"]), 2)

    def test_duplicates_skip_unique_sizes(self):
        first = self.file("one", b"same")
        second = self.file("two", b"same")
        self.file("unique", b"long unique content")
        self.file("same-size-different", b"else")
        tool = next(t for t in core.catalog() if t["operation"] == "duplicates")
        with mock.patch.object(core, "digest", wraps=core.digest) as hashed:
            rows = core.common(tool, core.discover([self.inputs]), None)
        self.assertEqual(hashed.call_count, 3)
        self.assertEqual(rows[0]["paths"], [str(first), str(second)])
        self.assertEqual(len(rows), 1)

    def test_manifest_response_roundtrip(self):
        self.file("nested/unicodé\nfile")
        manifest = self.work / "manifest.json"
        manifest.write_text(self.cli("hash-manifest", self.inputs).stdout)
        self.cli("hash-verify", "--manifest", manifest, self.inputs)
        self.file("nested/unicodé\nfile", b"modified")
        self.cli("hash-verify", "--manifest", manifest, self.inputs, code=1)

    def test_manifest_rejects_ambiguous_generation(self):
        self.file()
        other = self.work / "other"
        other.mkdir()
        (other / "sample.bin").write_bytes(b"another root")
        result = self.cli("hash-manifest", self.inputs, other, code=1)
        self.assertIn("ambiguous duplicate relative paths", result.stderr)
        self.assertEqual(result.stdout, "")

    def test_manifest_rejects_bad_schema(self):
        self.file()
        valid = {"path": "sample.bin", "sha256": "a" * 64, "bytes": 12}
        cases = [
            None,
            3,
            "not a manifest",
            [3],
            [{}],
            [dict(valid, path="../escape")],
            [dict(valid, path="/absolute")],
            [dict(valid, path="a//b")],
            [dict(valid, path="./sample.bin")],
            [dict(valid, sha256="broken")],
            [dict(valid, bytes=True)],
            [dict(valid, bytes=-1)],
            [valid, valid],
            {"tool": "library-inventory", "results": [], "failures": []},
            {"tool": "hash-manifest", "results": [], "failures": ["failed"]},
        ]
        manifest = self.work / "manifest.json"
        for data in cases:
            with self.subTest(data=data):
                manifest.write_text(json.dumps(data))
                result = self.cli(
                    "hash-verify", "--manifest", manifest, self.inputs, code=1
                )
                self.assertNotIn("Traceback", result.stderr)

    def test_manifest_accepts_uppercase_checksum(self):
        self.file()
        rows = json.loads(self.cli("hash-manifest", self.inputs).stdout)["results"]
        rows[0]["sha256"] = rows[0]["sha256"].upper()
        manifest = self.work / "manifest.json"
        manifest.write_text(json.dumps(rows))
        self.cli("hash-verify", "--manifest", manifest, self.inputs)

    def test_ordered_work_bounds_input_consumption(self):
        consumed = 0
        received = 0

        def items():
            nonlocal consumed
            for value in range(100):
                consumed += 1
                self.assertLessEqual(consumed - received, 4)
                yield value

        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
            for value in core.ordered_work(pool, lambda x: x * 2, items(), 4):
                self.assertEqual(value, received * 2)
                received += 1
        self.assertEqual(received, 100)

    def test_manifest_verify_and_mismatch(self):
        source = self.file()
        rows = json.loads(self.cli("hash-manifest", self.inputs).stdout)["results"]
        manifest = self.work / "manifest.json"
        manifest.write_text(json.dumps(rows))
        self.cli("hash-verify", "--manifest", manifest, self.inputs)
        source.write_bytes(b"changed")
        self.cli("hash-verify", "--manifest", manifest, self.inputs, code=1)

    def test_manifest_missing_and_extra(self):
        self.file()
        manifest = self.work / "manifest.json"
        manifest.write_text("[]")
        self.cli("hash-verify", "--manifest", manifest, self.inputs, code=1)

    def test_tree_diff(self):
        self.file()
        other = self.work / "other"
        other.mkdir()
        (other / "sample.bin").write_bytes(b"changed")
        result = json.loads(
            self.cli("tree-diff", "--against", other, self.inputs).stdout
        )
        self.assertEqual(result["results"][0]["status"], "changed")

    def test_paths(self):
        self.file("bad:name\n.bin")
        rows = json.loads(self.cli("path-audit", self.inputs).stdout)["results"]
        self.assertIn("control character", rows[0]["issues"])

    def test_no_inputs_and_bad_flags(self):
        self.cli("library-inventory", code=2)
        self.cli("library-inventory", "--not-a-flag", code=2)
        self.cli("unknown", code=2)

    def test_bad_jobs(self):
        for value in ("0", "33", "bad"):
            self.cli("library-inventory", "-j", value, self.inputs, code=2)

    def test_read_rejects_writes(self):
        self.file()
        self.cli("library-inventory", "--apply", self.inputs, code=2)

    def test_symlinks(self):
        source = self.file()
        link = self.work / "link"
        link.symlink_to(source)
        self.cli("library-inventory", link, code=1)
        nested = self.inputs / "nested"
        nested.symlink_to(self.home, target_is_directory=True)
        rows = json.loads(self.cli("library-inventory", self.inputs).stdout)["results"]
        self.assertEqual(len(rows), 1)

    def test_missing_and_empty(self):
        self.cli("library-inventory", self.work / "missing", code=1)
        self.cli("library-inventory", self.inputs, code=1)

    def test_config(self):
        self.file()
        config = self.work / "config.json"
        config.write_text(json.dumps({"roots": [str(self.inputs)], "jobs": 2}))
        self.cli("library-inventory", "--config", config)
        config.write_text("{ broken")
        self.cli("library-inventory", "--config", config, code=2)

    def test_logs_and_dry_run(self):
        self.file()
        log = self.work / "success.json"
        self.cli("library-inventory", "--dry-run", "-S", log, self.inputs)
        self.assertFalse(log.exists())
        self.cli("library-inventory", "-S", log, self.inputs)
        self.assertEqual(len(json.loads(log.read_text())), 1)
        self.cli("library-inventory", "-S", log, self.inputs, code=2)

    def test_atomic_failure(self):
        target = self.work / "output"

        def writer(p):
            p.write_bytes(b"data")

        def reject(p):
            raise ValueError("verification failed")

        with self.assertRaises(ValueError):
            core.publish(target, writer, reject)
        self.assertFalse(target.exists())
        self.assertEqual(list(self.work.glob(".utility-*")), [])

    def test_atomic_race(self):
        target = self.work / "output"

        def writer(p):
            p.write_bytes(b"new")
            target.write_bytes(b"other writer")

        with self.assertRaises(FileExistsError):
            core.publish(target, writer, lambda _: None)
        self.assertEqual(target.read_bytes(), b"other writer")

    def test_empty_output_supported(self):
        target = self.work / "empty"
        core.publish(target, lambda p: p.write_bytes(b""), lambda _: None)
        self.assertEqual(target.stat().st_size, 0)

    def test_mcp(self):
        self.file()
        requests = [
            {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2025-11-25",
                    "capabilities": {},
                    "clientInfo": {"name": "test", "version": "1"},
                },
            },
            {"jsonrpc": "2.0", "method": "notifications/initialized"},
            {"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
            {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {
                    "name": "library-inventory",
                    "arguments": {"paths": [str(self.inputs)]},
                },
            },
            {
                "jsonrpc": "2.0",
                "id": 4,
                "method": "tools/call",
                "params": {
                    "name": "library-inventory",
                    "arguments": {"paths": [str(self.home)]},
                },
            },
            {
                "jsonrpc": "2.0",
                "id": 5,
                "method": "tools/call",
                "params": {
                    "name": "library-inventory",
                    "arguments": {"paths": [str(self.inputs)], "apply": True},
                },
            },
        ]
        result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "mcp/server.py"),
                "--allow-root",
                str(self.inputs),
            ],
            input="\n".join(map(json.dumps, requests)) + "\n",
            capture_output=True,
            text=True,
            env=self.env,
            timeout=30,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        rows = [json.loads(row) for row in result.stdout.splitlines()]
        self.assertEqual(len(rows), 5)
        self.assertTrue(
            all(t["annotations"]["readOnlyHint"] for t in rows[1]["result"]["tools"])
        )
        self.assertFalse(rows[2]["result"]["isError"])
        self.assertTrue(rows[3]["result"]["isError"])
        self.assertTrue(rows[4]["result"]["isError"])

    def test_mcp_bad_json(self):
        result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "mcp/server.py"),
                "--allow-root",
                str(self.inputs),
            ],
            input="bad\n",
            capture_output=True,
            text=True,
            env=self.env,
            timeout=30,
        )
        self.assertEqual(json.loads(result.stdout)["error"]["code"], -32700)


if __name__ == "__main__":
    unittest.main()
