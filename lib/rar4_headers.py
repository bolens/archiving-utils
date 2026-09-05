"""Validate RAR4 headers, reject volumes, and collect independent payload CRC32."""

import zlib


def validate(source, max_members):
    entries = []
    main = False
    with source.open("rb") as stream:
        if stream.read(7) != b"Rar!\x1a\x07\x00":
            raise ValueError("unsupported legacy RAR signature")
        while True:
            header = stream.read(7)
            if len(header) != 7:
                raise ValueError("RAR4 archive has no complete end header")
            kind = header[2]
            flags = int.from_bytes(header[3:5], "little")
            size = int.from_bytes(header[5:7], "little")
            if size < 7:
                raise ValueError("invalid RAR4 header size")
            header += stream.read(size - 7)
            if len(header) != size or zlib.crc32(header[2:]) & 0xffff != int.from_bytes(header[:2], "little"):
                raise ValueError("RAR4 header checksum mismatch or truncation")
            if not main and kind != 0x73:
                raise ValueError("RAR4 main header is missing")
            if kind == 0x73:
                if main:
                    raise ValueError("duplicate RAR4 main header")
                main = True
                if flags & 1:
                    raise ValueError("multipart RAR4 archives are not supported")
                if flags & 0x80:
                    raise ValueError("encrypted RAR4 headers are not supported")
            packed = 0
            if flags & 0x8000:
                if size < 11:
                    raise ValueError("truncated RAR4 data size")
                packed = int.from_bytes(header[7:11], "little")
            if kind in (0x74, 0x7a):
                if size < 32 or not flags & 0x8000:
                    raise ValueError("truncated RAR4 file header")
                if flags & 3:
                    raise ValueError("split RAR4 entries are not supported")
                if flags & 4:
                    raise ValueError("encrypted RAR4 entries are not supported")
                if flags & 0x100:
                    if size < 40:
                        raise ValueError("truncated RAR4 large-file header")
                    packed |= int.from_bytes(header[32:36], "little") << 32
                if kind == 0x74:
                    entries.append((None, int.from_bytes(header[16:20], "little")))
                    if len(entries) > max_members:
                        raise ValueError("archive exceeds member limit")
            if kind == 0x7b:
                if flags & 1:
                    raise ValueError("multipart RAR4 archives are not supported")
                return entries
            stream.seek(packed, 1)
