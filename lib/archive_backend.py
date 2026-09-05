"""Optional native readers. Stream data through domain validation, never native extraction."""

import ctypes as c
import ctypes.util
import os
import stat
import zlib
from core import UsageError


def library():
    name = ctypes.util.find_library("archive")
    if not name:
        raise UsageError("missing dependency: libarchive (RAR, 7z and Zstandard TAR)")
    try:
        lib = c.CDLL(name)
        signatures = {
            "archive_read_new": (c.c_void_p, []),
            "archive_read_free": (c.c_int, [c.c_void_p]),
            "archive_read_open_filename": (c.c_int, [c.c_void_p, c.c_char_p, c.c_size_t]),
            "archive_read_next_header": (c.c_int, [c.c_void_p, c.POINTER(c.c_void_p)]),
            "archive_read_data": (c.c_ssize_t, [c.c_void_p, c.c_void_p, c.c_size_t]),
            "archive_error_string": (c.c_char_p, [c.c_void_p]),
            "archive_entry_pathname": (c.c_char_p, [c.c_void_p]),
            "archive_entry_size": (c.c_int64, [c.c_void_p]),
            "archive_entry_size_is_set": (c.c_int, [c.c_void_p]),
            "archive_entry_filetype": (c.c_uint, [c.c_void_p]),
            "archive_entry_hardlink": (c.c_char_p, [c.c_void_p]),
            "archive_entry_symlink": (c.c_char_p, [c.c_void_p]),
            "archive_entry_is_encrypted": (c.c_int, [c.c_void_p]),
        }
        for suffix in ("format_rar", "format_rar5", "format_7zip", "format_tar",
                       "filter_none", "filter_zstd"):
            signatures["archive_read_support_" + suffix] = (c.c_int, [c.c_void_p])
        for symbol, (result, args) in signatures.items():
            function = getattr(lib, symbol)
            function.restype, function.argtypes = result, args
    except (OSError, AttributeError) as error:
        raise UsageError("libarchive with RAR5, 7z and Zstandard support is required") from error
    return lib


def scan(source, consume, max_members):
    with source.open("rb") as header:
        magic = header.read(8)
    checksums = None
    rar5 = magic == b"Rar!\x1a\x07\x01\x00"
    if rar5:
        format_name = "rar5"
    elif magic.startswith(b"Rar!\x1a\x07\x00"):
        from rar4_headers import validate

        checksums = validate(source, max_members)
        format_name = "rar"
    elif magic.startswith(b"7z\xbc\xaf\x27\x1c"):
        format_name = "7zip"
    elif magic.startswith(b"\x28\xb5\x2f\xfd"):
        format_name = "tar"
    else:
        raise ValueError("unsupported native archive signature")
    if rar5:
        from rar5_checksums import entries

        checksums = entries(source, max_members)
    lib = library()
    handle = lib.archive_read_new()
    if not handle:
        raise MemoryError("cannot allocate archive reader")

    def check(status):
        if status != 0:
            message = lib.archive_error_string(handle)
            raise ValueError("archive decoder: " + (os.fsdecode(message) if message else str(status)))

    class Stream:
        crc = 0

        def read(self, size):
            buffer = c.create_string_buffer(size)
            count = lib.archive_read_data(handle, buffer, size)
            if count < 0:
                check(count)
            data = buffer.raw[:count]
            self.crc = zlib.crc32(data, self.crc)
            return data

    try:
        for suffix in ("format_" + format_name, "filter_none"):
            check(getattr(lib, "archive_read_support_" + suffix)(handle))
        # A warning can indicate an external decompressor fallback. Refuse it.
        with source.open("rb") as source_stream:
            zstd = source_stream.read(4) == b"\x28\xb5\x2f\xfd"
        if zstd:
            status = lib.archive_read_support_filter_zstd(handle)
            if status != 0:
                raise UsageError("libarchive requires native Zstandard support")
        check(lib.archive_read_open_filename(handle, os.fsencode(source), 64 * 1024))
        entry = c.c_void_p()
        index = 0
        while True:
            status = lib.archive_read_next_header(handle, c.byref(entry))
            if status == 1:  # ARCHIVE_EOF
                break
            check(status)
            if lib.archive_entry_is_encrypted(entry):
                raise ValueError("encrypted archive entries are not supported")
            kind = lib.archive_entry_filetype(entry)
            if (kind not in (stat.S_IFREG, stat.S_IFDIR)
                    or lib.archive_entry_hardlink(entry) is not None
                    or lib.archive_entry_symlink(entry) is not None):
                raise ValueError("archive contains a link or special file")
            name = lib.archive_entry_pathname(entry)
            if name is None:
                raise ValueError("archive member has no representable filename")
            directory = kind == stat.S_IFDIR
            if not directory and not lib.archive_entry_size_is_set(entry):
                raise ValueError("archive member has no declared size")
            stream = Stream()
            consume(os.fsdecode(name), lib.archive_entry_size(entry), directory, stream)
            if checksums is not None:
                if index >= len(checksums):
                    raise ValueError("RAR decoded member count mismatch")
                declared_name = checksums[index][0]
                if declared_name is not None and declared_name.rstrip("/") != os.fsdecode(name).rstrip("/"):
                    raise ValueError("RAR header and decoded member names disagree")
                expected = checksums[index][1]
                if not directory and stream.crc != expected:
                    raise ValueError("RAR payload CRC32 mismatch")
            index += 1
        if checksums is not None and index != len(checksums):
            raise ValueError("RAR decoded member count mismatch")
    finally:
        lib.archive_read_free(handle)
