"""Comic archive creation, extraction and preservation on disposable fixtures."""

import ctypes
import ctypes.util
import hashlib
import json
from pathlib import Path
import binascii
import shutil
import subprocess
import tarfile
import unittest
from unittest import mock
import zipfile
import zlib
from test_common import Fixture, core
import archive_backend
import domain
from types import SimpleNamespace
import comics

FORMATS = ("cbz", "cb7", "cbt", "cbt-gz", "cbt-bz2", "cbt-xz", "cbt-zst")
NATIVE = bool(ctypes.util.find_library("archive") and shutil.which("bsdtar"))


class Comics(Fixture):
    def seed(self):
        # The container workflow deliberately treats image bytes as opaque.
        self.file("chapter/10.PNG", b"page ten")
        self.file("chapter/2.webp", b"page two")
        self.file("chapter/01.jpg", b"page one")
        self.file("ComicInfo.xml", b'<ComicInfo><Title>Fixture</Title></ComicInfo>')
        self.file("notes/雪 [*]\n.txt", bytes(range(256)))
        self.file("-cover.avif", b"cover")
        (self.inputs / "empty/nested").mkdir(parents=True)

    def snapshot(self, root):
        return {p.relative_to(root).as_posix(): None if p.is_dir() else p.read_bytes()
                for p in root.rglob("*")}

    def info(self, source):
        return json.loads(self.cli("comic-info", source).stdout)["results"][0]["result"]

    def rar_fixture(self, name):
        fixture = Path(__file__).parent / "fixtures/libarchive" / (name + ".rar.uu")
        lines = fixture.read_bytes().splitlines()
        start = next(i for i, line in enumerate(lines) if line.startswith(b"begin ")) + 1
        source = self.work / (name + ".cbr")
        source.write_bytes(b"".join(binascii.a2b_uu(line) for line in lines[start:] if line != b"end"))
        return source

    @unittest.skipUnless(NATIVE, "missing dependency: libarchive/bsdtar")
    def test_rar4_rar5_extraction_and_conversion(self):
        expected = json.loads((Path(__file__).parent / "fixtures/libarchive/expected.json").read_text())
        for name, members in expected.items():
            with self.subTest(format=name):
                source = self.rar_fixture(name)
                original = source.read_bytes()
                self.assertEqual(self.info(source)["page_count"], 0)
                restored = self.work / (name + "-extracted")
                self.cli("comic-extract", "--apply", "-o", restored, source)
                actual = {n: None if data is None else hashlib.sha256(data).hexdigest()
                          for n, data in self.snapshot(restored).items()}
                self.assertEqual(actual, members)
                for fmt in FORMATS:
                    target = self.work / (name + "." + fmt.replace("-", "."))
                    self.cli("comic-to-" + fmt, "--apply", "-o", target, source)
                    rows = json.loads(self.cli("archive-list", target).stdout)["results"][0]["result"]
                    self.assertEqual({r["name"]: None if r["directory"] else r["sha256"] for r in rows}, members)
                self.assertEqual(source.read_bytes(), original)

    @unittest.skipUnless(NATIVE, "missing dependency: libarchive/bsdtar")
    def test_rar_encryption_links_incomplete_volume_and_crc_fail_closed(self):
        names = ("test_read_format_rar", "test_read_format_rar4_encrypted",
                 "test_read_format_rar5_encrypted", "test_read_format_rar5_hardlink",
                 "test_read_format_rar5_multiarchive.part01")
        sources = [self.rar_fixture(name) for name in names]
        corrupt = self.rar_fixture("test_read_format_rar5_stored")
        raw = corrupt.read_bytes()
        self.assertIn(b"hello libarchive", raw)
        corrupt.write_bytes(raw.replace(b"hello libarchive", b"jello libarchive"))
        sources.append(corrupt)
        for index, source in enumerate(sources):
            with self.subTest(source=source.name):
                before = source.read_bytes()
                target = self.work / ("rejected-" + str(index))
                self.cli("comic-extract", "--apply", "-o", target, source, code=1)
                self.assertFalse(target.exists())
                self.assertEqual(list(self.work.glob(".extract-*")), [])
                self.assertEqual(source.read_bytes(), before)

    def test_standard_creation_extraction_and_inventory(self):
        self.seed()
        expected = self.snapshot(self.inputs)
        for fmt in ("cbz", "cbt", "cbt-gz", "cbt-bz2", "cbt-xz"):
            with self.subTest(format=fmt):
                archive = self.work / ("comic." + fmt.replace("-", "."))
                self.cli("folder-to-" + fmt, "-o", archive, self.inputs)
                self.assertFalse(archive.exists())
                self.cli("folder-to-" + fmt, "--apply", "-o", archive, self.inputs)
                before = archive.read_bytes()
                result = self.info(archive)
                self.assertEqual([p["name"] for p in result["pages"]],
                                 ["-cover.avif", "chapter/01.jpg", "chapter/2.webp", "chapter/10.PNG"])
                self.assertEqual(result["page_count"], 4)
                self.assertEqual(result["metadata_files"], ["ComicInfo.xml"])
                hashes = {row["name"]: row["sha256"] for row in result["pages"] + result["other_files"]}
                self.assertEqual(hashes, {name: hashlib.sha256(data).hexdigest()
                                         for name, data in expected.items() if data is not None})
                target = self.work / (fmt + "-extracted")
                self.cli("comic-extract", "--apply", "-o", target, archive)
                self.assertEqual(self.snapshot(target), expected)
                self.assertEqual(archive.read_bytes(), before)
                self.assertEqual(self.snapshot(self.inputs), expected)
                self.cli("comic-extract", "--apply", "-o", target, archive, code=1)
                self.assertEqual(self.snapshot(target), expected)

    @unittest.skipUnless(NATIVE, "missing dependency: libarchive/bsdtar")
    def test_every_creation_and_cross_conversion(self):
        self.seed()
        expected = self.snapshot(self.inputs)
        for source_fmt in FORMATS:
            source = self.work / ("original." + source_fmt.replace("-", "."))
            self.cli("folder-to-" + source_fmt, "--apply", "-o", source, self.inputs)
            original = source.read_bytes()
            for target_fmt in FORMATS:
                with self.subTest(source=source_fmt, target=target_fmt):
                    target = self.work / (source_fmt + "-to-" + target_fmt + "." + target_fmt.replace("-", "."))
                    self.cli("comic-to-" + target_fmt, "--apply", "-o", target, source)
                    self.cli("comic-verify", target)
                    restored = self.work / (source_fmt + "-" + target_fmt + "-restored")
                    self.cli("comic-extract", "--apply", "-o", restored, target)
                    self.assertEqual(self.snapshot(restored), expected)
                    self.assertEqual(source.read_bytes(), original)
            self.assertEqual(self.snapshot(self.inputs), expected)

    def test_all_page_extensions_and_zero_pages(self):
        expected = {".jpg", ".jpeg", ".jpe", ".jfif", ".png", ".apng", ".webp", ".gif",
                    ".tif", ".tiff", ".bmp", ".dib", ".avif", ".heic", ".heif", ".jxl",
                    ".jp2", ".j2k", ".jpf", ".jpx", ".ppm", ".pgm", ".pbm", ".pnm", ".qoi"}
        names = ["p" + ext.upper() for ext in expected]
        rows = [{"name": name, "directory": False, "bytes": 1, "sha256": "x"} for name in names]
        result = comics.inventory(rows)
        self.assertEqual(result["page_count"], len(names))
        self.assertEqual({page["name"] for page in result["pages"]}, set(names))
        empty = self.work / "no-pages.cbz"
        with zipfile.ZipFile(empty, "w") as archive:
            archive.writestr("notes.txt", "not a page")
        self.assertEqual(self.info(empty)["page_count"], 0)

    def test_unsafe_members_and_partial_extraction_cleanup(self):
        for index, name in enumerate(("../escape", "/absolute", "a/../../escape", "a\\b", "C:drive")):
            source = self.work / (str(index) + ".cbz")
            with zipfile.ZipFile(source, "w") as archive:
                archive.writestr("good.png", b"first valid entry")
                archive.writestr(name, b"bad")
            target = self.work / ("failed-" + str(index))
            self.cli("comic-extract", "--apply", "-o", target, source, code=1)
            self.assertFalse(target.exists())
            self.assertEqual(list(self.work.glob(".extract-*")), [])
            self.cli("comic-to-cbz", "--apply", "-o", self.work / (str(index) + "-bad.cbz"), source, code=1)
        self.assertFalse((self.work / "escape").exists())

    @unittest.skipUnless(NATIVE, "missing dependency: libarchive/bsdtar")
    def test_native_links_limits_and_corruption(self):
        self.seed()
        source = self.work / "book.cb7"
        self.cli("folder-to-cb7", "--apply", "-o", source, self.inputs)
        self.cli("comic-verify", "--max-members", 1, source, code=1)
        self.cli("comic-verify", "--max-bytes", 1, source, code=1)
        corrupt = self.work / "broken.cb7"
        corrupt.write_bytes(source.read_bytes()[:40])
        self.cli("comic-verify", corrupt, code=1)
        linked = self.work / "links"
        linked.mkdir()
        (linked / "page.jpg").symlink_to(self.inputs / "chapter/01.jpg")
        unsafe = self.work / "link.cb7"
        subprocess.run(["bsdtar", "-c", "--format=7zip", "-f", str(unsafe), "-C", str(linked), "."],
                       check=True, capture_output=True, env=self.env, timeout=30)
        self.cli("comic-extract", "--apply", "-o", self.work / "unsafe", unsafe, code=1)
        self.assertFalse((self.work / "unsafe").exists())

    def test_missing_backend_and_unsupported_ace(self):
        with mock.patch.object(ctypes.util,
                               "find_library", return_value=None):
            with self.assertRaises(core.UsageError):
                archive_backend.library()
        source = self.file("legacy.cba", b"ACE")
        result = self.cli("comic-info", source, code=1)
        self.assertIn("CBA/ACE", result.stdout)

    @unittest.skipUnless(NATIVE and ctypes.util.find_library("zstd"), "missing native Zstandard backend")
    def test_zstandard_wrapped_rar_cannot_bypass_crc(self):
        source = self.rar_fixture("test_read_format_rar5_stored")
        payload = source.read_bytes().replace(b"hello libarchive", b"jello libarchive")
        lib = ctypes.CDLL(ctypes.util.find_library("zstd"))
        lib.ZSTD_compressBound.argtypes = [ctypes.c_size_t]
        lib.ZSTD_compressBound.restype = ctypes.c_size_t
        lib.ZSTD_compress.argtypes = [ctypes.c_void_p, ctypes.c_size_t, ctypes.c_void_p, ctypes.c_size_t, ctypes.c_int]
        lib.ZSTD_compress.restype = ctypes.c_size_t
        capacity = lib.ZSTD_compressBound(len(payload))
        buffer = ctypes.create_string_buffer(capacity)
        count = lib.ZSTD_compress(buffer, capacity, payload, len(payload), 1)
        self.assertLessEqual(count, capacity)
        wrapped = self.work / "wrapped.cbt.zst"
        wrapped.write_bytes(buffer.raw[:count])
        self.cli("comic-verify", wrapped, code=1)
        for tool, suffix in (("comic-extract", "directory"), ("comic-to-cbz", "cbz")):
            target = self.work / ("rejected." + suffix)
            self.cli(tool, "--apply", "-o", target, wrapped, code=1)
            self.assertFalse(target.exists())

    @unittest.skipUnless(NATIVE, "missing dependency: libarchive/bsdtar")
    def test_stored_rar4_crc_is_checked_before_publication(self):
        source = self.rar_fixture("test_read_format_rar_windows")
        raw = bytearray(source.read_bytes())
        # First file's stored payload starts at 7 + 13 + 67 in this pinned fixture.
        self.assertEqual(raw[87:103], b"test text file\r\n")
        raw[87] ^= 1
        source.write_bytes(raw)
        self.cli("comic-verify", source, code=1)
        for tool, suffix in (("comic-extract", "directory"), ("comic-to-cbz", "cbz")):
            target = self.work / ("corrupt-rar4." + suffix)
            self.cli(tool, "--apply", "-o", target, source, code=1)
            self.assertFalse(target.exists())
        self.assertEqual(source.read_bytes(), raw)

    @unittest.skipUnless(NATIVE, "missing dependency: libarchive/bsdtar")
    def test_rar4_complete_member_volume_is_not_published(self):
        source = self.rar_fixture("test_read_format_rar_windows")
        data = bytearray(source.read_bytes())
        offset = 7
        while offset < len(data):
            size = int.from_bytes(data[offset + 5:offset + 7], "little")
            kind = data[offset + 2]
            flags = int.from_bytes(data[offset + 3:offset + 5], "little")
            packed = int.from_bytes(data[offset + 7:offset + 11], "little") if flags & 0x8000 else 0
            if kind in (0x73, 0x7b):
                flags |= 0x101 if kind == 0x73 else 1
                data[offset + 3:offset + 5] = flags.to_bytes(2, "little")
                crc = zlib.crc32(data[offset + 2:offset + size]) & 0xffff
                data[offset:offset + 2] = crc.to_bytes(2, "little")
            offset += size + packed
        source.write_bytes(data)
        self.cli("comic-verify", source, code=1)
        for tool, suffix in (("comic-extract", "directory"), ("comic-to-cbz", "cbz")):
            target = self.work / ("volume." + suffix)
            self.cli(tool, "--apply", "-o", target, source, code=1)
            self.assertFalse(target.exists())
        self.assertEqual(source.read_bytes(), data)

    def test_explicit_output_name_does_not_change_encoder(self):
        self.seed()
        target = self.work / "misnamed.cba"
        self.cli("folder-to-cbz", "--apply", "-o", target, self.inputs)
        self.assertTrue(zipfile.is_zipfile(target))
        self.assertEqual(self.info(target)["page_count"], 4)

    def test_creation_missing_writer_leaves_no_output(self):
        self.seed()
        target = self.work / "missing.cb7"
        with mock.patch.dict(self.env, {"PATH": ""}):
            result = self.cli("folder-to-cb7", "--apply", "-o", target, self.inputs, code=2)
        self.assertIn("missing dependency: bsdtar", result.stdout)
        self.assertFalse(target.exists())
        self.assertEqual(list(self.work.glob(".utility-*")), [])

    def test_native_writer_partial_output_and_directory_loss_are_rejected(self):
        self.seed()
        original = self.snapshot(self.inputs)
        args = SimpleNamespace(max_members=1000, max_bytes=100000)
        for mode in ("partial", "lost-directories"):
            target = self.work / (mode + ".cb7")

            def broken_writer(command):
                temporary = Path(command[command.index("-f") + 1])
                if mode == "partial":
                    temporary.write_bytes(b"incomplete archive")
                else:
                    with zipfile.ZipFile(temporary, "w") as archive:
                        for path in self.inputs.rglob("*"):
                            if path.is_file():
                                archive.write(path, path.relative_to(self.inputs).as_posix())

            with self.subTest(mode=mode), mock.patch.object(domain, "run", side_effect=broken_writer):
                with self.assertRaises((ValueError, tarfile.TarError)):
                    domain.pack(self.inputs, target, "7z", args)
            self.assertFalse(target.exists())
            self.assertEqual(list(self.work.glob(".utility-*")), [])
            self.assertEqual(self.snapshot(self.inputs), original)

    def test_comic_batch_partial_failure(self):
        good = self.inputs / "good.CBZ"
        with zipfile.ZipFile(good, "w") as archive:
            archive.writestr("01.png", b"page")
        bad = self.file("bad.cbz", b"broken")
        for jobs in (1, 2):
            target = self.work / ("batch" + str(jobs))
            result = json.loads(self.cli("comic-to-cbt", "--apply", "-j", jobs,
                                         "--output-dir", target, self.inputs, code=1).stdout)
            self.assertEqual([r["path"] for r in result["results"]], [str(good)])
            self.assertEqual([r["path"] for r in result["failures"]], [str(bad)])
            self.assertEqual(len(list(target.iterdir())), 1)
            self.assertEqual(bad.read_bytes(), b"broken")


if __name__ == "__main__":
    unittest.main()
