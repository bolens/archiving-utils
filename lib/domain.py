"""Archive operations with bounded, regular-file-only extraction."""

import bz2
import gzip
import hashlib
import lzma
import os
from pathlib import Path, PurePosixPath
import shutil
import stat
import tarfile
import tempfile
import zipfile
from core import discover, digest, publish, regular

COMPRESSORS = {"gz": gzip, "bz2": bz2, "xz": lzma}
TAR_MODES = {"tar": "", "tar.gz": "gz", "tar.bz2": "bz2", "tar.xz": "xz"}


def member_name(name):
    path = PurePosixPath(name)
    if (
        not name
        or path.is_absolute()
        or ".." in path.parts
        or "\\" in name
        or "\x00" in name
        or ":" in name
    ):
        raise ValueError("unsafe archive member: " + repr(name))
    if str(path) in (".", ""):
        raise ValueError("empty archive member")
    return path


def scan(source, args, sink=None):
    result, seen, total = [], set(), 0

    def consume(name, size, directory, stream):
        nonlocal total
        if directory and name in (".", "./"):
            return
        path = member_name(name)
        key = str(path)
        if key in seen:
            raise ValueError("duplicate archive member: " + repr(name))
        seen.add(key)
        if len(seen) > args.max_members or size < 0 or total + size > args.max_bytes:
            raise ValueError("archive exceeds member or uncompressed-byte limit")
        total += size
        row = {"name": key, "bytes": size, "directory": directory}
        if not directory:
            h = hashlib.sha256()
            count = 0
            target = sink / path if sink else None
            if target:
                target.parent.mkdir(parents=True, exist_ok=True)
            output = target.open("xb") if target else None
            try:
                while chunk := stream.read(
                    min(1024 * 1024, args.max_bytes - count + 1)
                ):
                    count += len(chunk)
                    if count > size or count > args.max_bytes:
                        raise ValueError("member exceeds declared size or limit")
                    h.update(chunk)
                    if output:
                        output.write(chunk)
                if count != size:
                    raise ValueError("truncated archive member")
            finally:
                if output:
                    output.close()
            row["sha256"] = h.hexdigest()
        elif sink:
            (sink / path).mkdir(parents=True, exist_ok=True)
        result.append(row)

    if zipfile.is_zipfile(source):
        with zipfile.ZipFile(source) as archive:
            for member in archive.infolist():
                mode = member.external_attr >> 16
                if stat.S_ISLNK(mode) or (
                    stat.S_IFMT(mode) not in (0, stat.S_IFREG, stat.S_IFDIR)
                ):
                    raise ValueError("archive contains a link or special file")
                if member.flag_bits & 1:
                    raise ValueError("encrypted ZIP is not supported")
                with archive.open(member) as stream:
                    consume(member.filename, member.file_size, member.is_dir(), stream)
    else:
        with tarfile.open(source, "r:*") as archive:
            for member in archive:
                if not (member.isfile() or member.isdir()):
                    raise ValueError("archive contains a link or special file")
                if member.isfile():
                    with archive.extractfile(member) as stream:
                        consume(member.name, member.size, False, stream)
                else:
                    consume(member.name, 0, True, None)
    return result


def pack(source, target, format_name, args):
    files = discover([source])
    # Do not silently omit source links or special nodes from preservation packages.
    for parent, dirs, names in os.walk(source, followlinks=False):
        for name in dirs + names:
            p = Path(parent) / name
            if p.is_symlink() or not (p.is_file() or p.is_dir()):
                raise ValueError(
                    "packing links or special files is not supported: " + str(p)
                )
    if (
        sum(p.stat().st_size for p, _ in files) > args.max_bytes
        or len(files) > args.max_members
    ):
        raise ValueError("source exceeds archive limits")
    # Include empty directories. Sort names for stable member order.
    directories = sorted(
        (p for p in source.rglob("*") if p.is_dir()), key=lambda p: os.fsencode(p)
    )
    if len(files) + len(directories) > args.max_members:
        raise ValueError("source exceeds member limit")
    for p in directories:
        member_name(p.relative_to(source).as_posix())
    for _, rel in files:
        member_name(rel.as_posix())
    expected = {str(rel): digest(p) for p, rel in files}

    def writer(temp):
        if format_name == "zip":
            with zipfile.ZipFile(
                temp, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6
            ) as archive:
                for p in directories:
                    archive.write(p, p.relative_to(source).as_posix() + "/")
                for p, rel in files:
                    archive.write(p, rel.as_posix())
        else:
            with tarfile.open(
                temp, "w:" + TAR_MODES[format_name], format=tarfile.PAX_FORMAT
            ) as archive:
                for p in directories:
                    archive.add(
                        p, arcname=p.relative_to(source).as_posix(), recursive=False
                    )
                for p, rel in files:
                    archive.add(p, arcname=rel.as_posix(), recursive=False)

    def verify(temp):
        actual = {
            row["name"]: row["sha256"]
            for row in scan(temp, args)
            if not row["directory"]
        }
        if expected != actual:
            raise ValueError("archive round-trip checksum mismatch")

    publish(target, writer, verify)


def extract(source, target, args):
    target = regular(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        raise FileExistsError("extraction destination exists")
    with tempfile.TemporaryDirectory(prefix=".extract-", dir=target.parent) as temp:
        stage = Path(temp) / "contents"
        stage.mkdir()
        scan(source, args, stage)
        # Linux renameat2 with RENAME_NOREPLACE prevents concurrent directory replacement.
        import ctypes

        libc = ctypes.CDLL(None, use_errno=True)
        rename = libc.renameat2
        rename.argtypes = [
            ctypes.c_int,
            ctypes.c_char_p,
            ctypes.c_int,
            ctypes.c_char_p,
            ctypes.c_uint,
        ]
        if rename(-100, os.fsencode(stage), -100, os.fsencode(target), 1):
            err = ctypes.get_errno()
            raise OSError(err, os.strerror(err), str(target))


def decompressed(source, compressor, args, target=None):
    total = 0
    h = hashlib.sha256()
    output = target.open("xb") if target else None
    try:
        with compressor.open(source, "rb") as stream:
            while chunk := stream.read(1024 * 1024):
                total += len(chunk)
                if total > args.max_bytes:
                    raise ValueError("decompressed data exceeds byte limit")
                h.update(chunk)
                if output:
                    output.write(chunk)
    finally:
        if output:
            output.close()
    return {"bytes": total, "sha256": h.hexdigest()}


def inspect(tool, source, args):
    op = tool["operation"]
    if op == "compression-test":
        return decompressed(source, COMPRESSORS[tool["format"]], args)
    rows = scan(source, args)
    if op == "list":
        return rows
    if op == "verify":
        return {
            "verified": True,
            "members": len(rows),
            "bytes": sum(r["bytes"] for r in rows),
        }
    if op == "stats":
        size = source.stat().st_size
        total = sum(r["bytes"] for r in rows)
        return {
            "members": len(rows),
            "stored_bytes": size,
            "expanded_bytes": total,
            "expansion_ratio": round(total / max(size, 1), 3),
        }
    if op == "archive-manifest":
        return {r["name"]: r["sha256"] for r in rows if not r["directory"]}
    raise ValueError("unsupported operation: " + op)


def write(tool, source, target, args):
    op = tool["operation"]
    if op == "pack":
        return pack(source, target, tool["format"], args)
    if op == "extract":
        return extract(source, target, args)
    if op == "repack":
        with tempfile.TemporaryDirectory(prefix="archive-repack-") as temp:
            stage = Path(temp) / "contents"
            stage.mkdir()
            scan(source, args, stage)
            return pack(stage, target, tool["format"], args)
    compressor = COMPRESSORS[tool["format"]]
    if op == "compress":
        expected = digest(source)
        if source.stat().st_size > args.max_bytes:
            raise ValueError("source exceeds byte limit")

        def writer(temp):
            with source.open("rb") as src, compressor.open(temp, "wb") as dst:
                shutil.copyfileobj(src, dst)

        def verify(temp):
            if decompressed(temp, compressor, args)["sha256"] != expected:
                raise ValueError("compression checksum mismatch")

        return publish(target, writer, verify)
    if op == "decompress":
        expected = decompressed(source, compressor, args)["sha256"]

        def verify(temp):
            if digest(temp) != expected:
                raise ValueError("decompression checksum mismatch")

        return publish(
            target, lambda temp: decompressed(source, compressor, args, temp), verify
        )
    raise ValueError("unsupported operation: " + op)
