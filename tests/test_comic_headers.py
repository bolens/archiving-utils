"""Header guards tested directly, with no optional native backend."""

import binascii
from pathlib import Path
import unittest
import zlib
from test_common import Fixture
import rar4_headers
import rar5_checksums


def number(value):
    result = bytearray()
    while value >= 128:
        result.append((value & 127) | 128)
        value >>= 7
    return bytes(result + bytes([value]))


def block(data):
    body = number(len(data)) + data
    return zlib.crc32(body).to_bytes(4, "little") + body


class ComicHeaders(Fixture):
    def source(self, raw):
        return self.file("book.cbr", raw)

    def fixture(self, name):
        raw = (Path(__file__).parent / "fixtures/libarchive" / (name + ".rar.uu")).read_bytes().splitlines()
        start = next(i for i, line in enumerate(raw) if line.startswith(b"begin ")) + 1
        return self.source(b"".join(binascii.a2b_uu(line) for line in raw[start:] if line != b"end"))

    def test_rar5_reference_names_and_crc_values(self):
        for name, expected in (("test_read_format_rar5_stored", "helloworld.txt"),
                               ("test_read_format_rar5_compressed", "test.bin")):
            with self.subTest(fixture=name):
                rows = rar5_checksums.entries(self.fixture(name), 100)
                self.assertEqual(len(rows), 1)
                self.assertEqual(rows[0][0], expected)
                self.assertIsInstance(rows[0][1], int)
        with self.assertRaisesRegex(ValueError, "member limit"):
            rar5_checksums.entries(self.fixture("test_read_format_rar5_stored"), 0)

    def test_rar5_crc_less_files_refused_and_zero_crc_retained(self):
        magic = b"Rar!\x1a\x07\x01\x00"
        main = block(b"\x01\x00\x00")
        end = block(b"\x05\x00\x00")
        # File: type, header flags, file flags, size, attrs, [CRC], method, OS, name.
        without_crc = block(b"\x02\x00\x00\x00\x00\x00\x01\x01x")
        with self.assertRaisesRegex(ValueError, "without CRC32"):
            rar5_checksums.entries(self.source(magic + main + without_crc + end), 10)
        zero_crc = block(b"\x02\x00\x04\x00\x00" + bytes(4) + b"\x00\x01\x01x")
        self.assertEqual(rar5_checksums.entries(self.source(magic + main + zero_crc + end), 10), [("x", 0)])

    def test_rar5_truncation_bad_crc_oversized_and_missing_end(self):
        valid = self.fixture("test_read_format_rar5_stored").read_bytes()
        bad_crc = bytearray(valid)
        bad_crc[8] ^= 1
        for raw in (valid[:8], valid[:11], valid[:-1], bytes(bad_crc),
                    valid[:8] + bytes(4) + b"\x80\x80\x80",
                    valid[:8] + bytes(4) + b"\x7f" + b"short"):
            with self.subTest(size=len(raw)), self.assertRaises(ValueError):
                rar5_checksums.entries(self.source(raw), 10)
        # A CRC-valid main header without an end marker must still fail.
        with self.assertRaisesRegex(ValueError, "end header"):
            rar5_checksums.entries(self.source(valid[:8] + block(b"\x01\x00\x00")), 10)

    def test_rar5_volume_header_and_bad_variable_integer(self):
        magic = b"Rar!\x1a\x07\x01\x00"
        with self.assertRaisesRegex(ValueError, "multipart"):
            rar5_checksums.entries(self.source(magic + block(b"\x01\x00\x01")), 10)
        for raw in (b"", b"\x80", b"\x80" * 10):
            with self.subTest(raw=raw), self.assertRaises(ValueError):
                rar5_checksums.vint(raw, 0)

    def test_rar4_reference_crc_and_header_rejection(self):
        source = self.fixture("test_read_format_rar_windows")
        valid = source.read_bytes()
        rows = rar4_headers.validate(source, 10)
        self.assertEqual(len(rows), 5)
        self.assertEqual(rows[0][1], zlib.crc32(b"test text file\r\n"))
        for raw in (valid[:7], valid[:10], valid[:-1], valid[:7] + b"\x00" + valid[8:]):
            with self.subTest(size=len(raw)), self.assertRaises(ValueError):
                rar4_headers.validate(self.source(raw), 10)
        with self.assertRaisesRegex(ValueError, "member limit"):
            rar4_headers.validate(self.source(valid), 0)


if __name__ == "__main__":
    unittest.main()
