from pathlib import Path
import json
import io
import tarfile
import zipfile
import unittest
from test_common import Fixture


class Archive(Fixture):
    def test_mixed_batch_preserves_success_and_reports_failure(self):
        source = self.inputs / "good.zip"
        with zipfile.ZipFile(source, "w") as archive:
            archive.writestr("kept.bin", b"preserved")
        corrupt = self.file("00-corrupt.zip", b"invalid input")
        before = {path: path.read_bytes() for path in (source, corrupt)}
        for jobs in (1, 2):
            with self.subTest(jobs=jobs):
                output = self.work / ("batch-" + str(jobs))
                success_log = self.work / ("success-" + str(jobs) + ".json")
                failure_log = self.work / ("failure-" + str(jobs) + ".json")
                response = json.loads(self.cli(
                    "archive-extract", "--apply", "-j", jobs, "--output-dir", output,
                    "-S", success_log, "-L", failure_log, self.inputs, code=1,
                ).stdout)
                self.assertEqual([r["path"] for r in response["results"]], [str(source)])
                self.assertEqual([r["path"] for r in response["failures"]], [str(corrupt)])
                self.assertEqual(response["results"][0]["status"], "written")
                self.assertEqual(response["failures"][0]["status"], "failed")
                self.assertEqual(json.loads(success_log.read_text()), response["results"])
                self.assertEqual(json.loads(failure_log.read_text()), response["failures"])
                published = Path(response["results"][0]["output"])
                self.assertEqual((published / "kept.bin").read_bytes(), b"preserved")
                self.assertFalse(Path(response["failures"][0]["output"]).exists())
                self.assertEqual(list(output.iterdir()), [published])
                for path, original in before.items():
                    self.assertEqual(path.read_bytes(), original)

    def seed(self):
        self.file("space [1]\n.bin", b"data" * 200)
        self.file("-dash.bin", b"more data")
        self.file("empty.bin", b"")
        (self.inputs / "empty-directory").mkdir()
        self.file("nested/雪 [*]\n.bin", bytes(range(256)))
        (self.inputs / "nested/empty/deeper").mkdir(parents=True)

    def test_exclude_corrupt_archive_from_extraction_batch(self):
        archive = self.inputs / "good.zip"
        with zipfile.ZipFile(archive, "w") as packed:
            packed.writestr("kept.bin", b"preserved")
        ignored = self.file("skip-corrupt.zip", b"invalid archive")
        output = self.work / "selected-output"
        self.cli(
            "archive-extract",
            "--exclude",
            "skip*",
            "--apply",
            "--output-dir",
            output,
            self.inputs,
        )
        self.assertEqual(list(output.rglob("kept.bin"))[0].read_bytes(), b"preserved")
        self.assertEqual(ignored.read_bytes(), b"invalid archive")
        self.assertTrue(archive.is_file())

    def test_all_pack_repack_and_reports(self):
        self.seed()

        def snapshot(root):
            return {
                p.relative_to(root).as_posix(): None if p.is_dir() else p.read_bytes()
                for p in root.rglob("*")
            }

        expected = snapshot(self.inputs)
        for fmt in ("zip", "tar", "tar-gz", "tar-bz2", "tar-xz"):
            with self.subTest(format=fmt):
                suffix = fmt.replace("-", ".")
                archive = self.work / ("archive." + suffix)
                self.cli(
                    "folder-to-" + fmt, "--apply", "--output", archive, self.inputs
                )
                self.cli("archive-verify", archive)
                for tool in ("archive-list", "archive-stats", "archive-manifest"):
                    self.cli(tool, archive)
                extracted = self.work / ("extracted-" + fmt)
                self.cli("archive-extract", "--apply", "--output", extracted, archive)
                self.assertEqual(
                    (extracted / "space [1]\n.bin").read_bytes(), b"data" * 200
                )
                self.assertEqual(snapshot(extracted), expected)
                repacked = self.work / ("repacked." + suffix)
                self.cli("archive-to-" + fmt, "--apply", "--output", repacked, archive)
                self.cli("archive-verify", repacked)
                restored = self.work / ("restored-" + fmt)
                self.cli("archive-extract", "--apply", "-o", restored, repacked)
                self.assertEqual(snapshot(restored), expected)
                self.assertEqual(snapshot(self.inputs), expected)

    def test_compression_roundtrips(self):
        for payload in (b"compress me" * 1000, b""):
            source = self.file("payload-" + str(len(payload)) + ".bin", payload)
            for fmt in ("gz", "bz2", "xz"):
                with self.subTest(format=fmt, size=len(payload)):
                    out = self.work / (source.name + "." + fmt)
                    self.cli("file-to-" + fmt, "--apply", "--output", out, source)
                    self.cli(fmt + "-verify", out)
                    decoded = self.work / (source.name + "." + fmt + ".decoded")
                    self.cli(fmt + "-to-file", "--apply", "--output", decoded, out)
                    self.assertEqual(decoded.read_bytes(), payload)

    def test_dry_run_collision_and_source_retention(self):
        source = self.file()
        target = self.work / "data.gz"
        self.cli("file-to-gz", "--output", target, source)
        self.assertFalse(target.exists())
        self.cli("file-to-gz", "--apply", "--dry-run", "--output", target, source)
        self.assertFalse(target.exists())
        self.cli("file-to-gz", "--apply", "--output", target, source)
        self.assertTrue(source.exists())
        original = target.read_bytes()
        self.cli("file-to-gz", "--apply", "--output", target, source, code=1)
        self.assertEqual(target.read_bytes(), original)

    def test_no_nested_pack_destination(self):
        self.file()
        self.cli(
            "folder-to-zip",
            "--apply",
            "-o",
            self.inputs / "bad.zip",
            self.inputs,
            code=2,
        )

    def test_malicious_zip_paths(self):
        for index, name in enumerate(
            ("../escape", "/absolute", "a/../../escape", "C:\\escape", "a\\escape")
        ):
            path = self.work / f"evil{index}.zip"
            with zipfile.ZipFile(path, "w") as z:
                z.writestr(name, b"bad")
            target = self.work / f"extract{index}"
            self.cli("archive-extract", "--apply", "-o", target, path, code=1)
            self.assertFalse(target.exists())
        self.assertFalse((self.work / "escape").exists())

    def test_conventional_tar_root_directory(self):
        archive = self.work / "root.tar"
        with tarfile.open(archive, "w") as t:
            root = tarfile.TarInfo("./")
            root.type = tarfile.DIRTYPE
            t.addfile(root)
            item = tarfile.TarInfo("./data")
            item.size = 4
            t.addfile(item, io.BytesIO(b"data"))
        target = self.work / "extracted"
        self.cli("archive-extract", "--apply", "-o", target, archive)
        self.assertEqual((target / "data").read_bytes(), b"data")

    def test_links_rejected(self):
        archive = self.work / "link.tar"
        with tarfile.open(archive, "w") as t:
            i = tarfile.TarInfo("link")
            i.type = tarfile.SYMTYPE
            i.linkname = "../escape"
            t.addfile(i)
        self.cli("archive-verify", archive, code=1)
        self.file()
        (self.inputs / "link").symlink_to(self.home)
        self.cli(
            "folder-to-zip",
            "--apply",
            "-o",
            self.work / "links.zip",
            self.inputs,
            code=1,
        )

    def test_duplicate_members_and_limits(self):
        archive = self.work / "big.zip"
        with zipfile.ZipFile(archive, "w") as z:
            z.writestr("data", b"x" * 200)
            z.writestr("other", b"other")
        self.cli("archive-verify", "--max-bytes", "20", archive, code=1)
        self.cli("archive-verify", "--max-members", "1", archive, code=1)
        duplicate = self.work / "dupe.tar"
        with tarfile.open(duplicate, "w") as t:
            for _ in range(2):
                i = tarfile.TarInfo("dupe")
                i.size = 1
                t.addfile(i, io.BytesIO(b"a"))
        self.cli("archive-verify", duplicate, code=1)

    def test_corrupt_archive_and_compressed_stream(self):
        for name, tool in [
            ("bad.zip", "archive-verify"),
            ("bad.gz", "gz-verify"),
            ("bad.bz2", "bz2-verify"),
            ("bad.xz", "xz-verify"),
        ]:
            path = self.file(name, b"corrupt")
            self.cli(tool, path, code=1)

    def test_parallel_outputs_and_collision(self):
        self.file("one.bin")
        self.file("two.bin")
        outputs = self.work / "outputs"
        self.cli(
            "file-to-gz", "--apply", "--output-dir", outputs, "-j", "2", self.inputs
        )
        self.assertEqual(len(list(outputs.iterdir())), 2)
        other = self.work / "other"
        other.mkdir()
        (other / "one.bin").write_bytes(b"other")
        self.cli(
            "file-to-gz",
            "--output-dir",
            self.work / "collisions",
            self.inputs,
            other,
            code=2,
        )


if __name__ == "__main__":
    unittest.main()
