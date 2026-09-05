"""Bounded RAR5 header/CRC metadata, independent of native decoder checksum handling.

Format: https://www.rarlab.com/technote.htm
Only single-volume, unencrypted files with declared sizes and CRC32 are accepted.
"""

import zlib


def vint(data, offset):
    value = 0
    for shift in range(0, 70, 7):
        if offset >= len(data):
            raise ValueError("truncated RAR5 variable integer")
        byte = data[offset]
        offset += 1
        value |= (byte & 127) << shift
        if byte < 128:
            return value, offset
    raise ValueError("oversized RAR5 variable integer")


def entries(source, max_members):
    result = []
    with source.open("rb") as stream:
        if stream.read(8) != b"Rar!\x1a\x07\x01\x00":
            raise ValueError("invalid RAR5 signature")
        while True:
            checksum = stream.read(4)
            if len(checksum) != 4:
                raise ValueError("RAR5 archive has no complete end header")
            encoded_size = bytearray()
            for _ in range(3):
                byte = stream.read(1)
                if not byte:
                    raise ValueError("truncated RAR5 header size")
                encoded_size.extend(byte)
                if byte[0] < 128:
                    break
            else:
                raise ValueError("RAR5 header exceeds size limit")
            size, _ = vint(encoded_size, 0)
            if size > 2 * 1024 * 1024:
                raise ValueError("RAR5 header exceeds size limit")
            data = stream.read(size)
            if len(data) != size or zlib.crc32(encoded_size + data) != int.from_bytes(checksum, "little"):
                raise ValueError("RAR5 header checksum mismatch or truncation")
            kind, offset = vint(data, 0)
            flags, offset = vint(data, offset)
            extra = packed = 0
            if flags & 1:
                extra, offset = vint(data, offset)
            if flags & 2:
                packed, offset = vint(data, offset)
            if flags & (8 | 16):
                raise ValueError("multipart RAR5 archives are not supported")
            if extra > size - offset:
                raise ValueError("invalid RAR5 extra area")
            if kind == 4:
                raise ValueError("encrypted RAR5 archives are not supported")
            if kind == 1:
                archive_flags, _ = vint(data, offset)
                if archive_flags & 1:
                    raise ValueError("multipart RAR5 archives are not supported")
            if kind == 2:
                file_flags, offset = vint(data, offset)
                _, offset = vint(data, offset)  # expanded size checked by shared consumer
                _, offset = vint(data, offset)  # attributes
                if file_flags & 8:
                    raise ValueError("RAR5 files require declared sizes")
                if file_flags & 2:
                    offset += 4
                crc = None
                if file_flags & 4:
                    if offset + 4 > len(data):
                        raise ValueError("truncated RAR5 file checksum")
                    crc = int.from_bytes(data[offset:offset + 4], "little")
                    offset += 4
                _, offset = vint(data, offset)  # compression
                _, offset = vint(data, offset)  # host OS
                length, offset = vint(data, offset)
                if offset + length > len(data) - extra:
                    raise ValueError("truncated RAR5 filename")
                name = data[offset:offset + length].decode("utf-8").replace("\\", "/")
                if not file_flags & 1 and crc is None:
                    raise ValueError("RAR5 files without CRC32 are not supported")
                result.append((name, crc))
                if len(result) > max_members:
                    raise ValueError("archive exceeds member limit")
            if kind == 5:
                end_flags, _ = vint(data, offset)
                if end_flags & 1:
                    raise ValueError("multipart RAR5 archives are not supported")
                return result
            stream.seek(packed, 1)
