"""Shared offline CLI: deterministic discovery, bounded workers, verified publication."""

import argparse
import concurrent.futures
from collections import Counter, deque
import hashlib
from fnmatch import fnmatchcase
import json
import os
import re
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
SUITE = ROOT.name


class UsageError(Exception):
    pass


def catalog():
    return json.loads((ROOT / "lib/catalog.json").read_text())


def run(command, timeout=3600):
    if not shutil.which(command[0]):
        raise UsageError("missing dependency: " + command[0])
    result = subprocess.run(
        command,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=timeout,
        check=False,
    )
    if result.returncode:
        raise RuntimeError(
            result.stderr.decode("utf-8", "replace")[-4000:] or "command failed"
        )
    return result.stdout


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def regular(path):
    # Preserve .. until every original component has been checked for symlinks.
    path = Path(path).absolute()
    normalized = Path(os.path.abspath(path))
    for candidate in (path, normalized):
        if any(p.is_symlink() for p in (candidate, *candidate.parents)):
            raise ValueError("symlink input is not supported: " + str(path))
    return normalized


def excluded(relative, patterns):
    return any(fnmatchcase(str(relative), pattern) for pattern in patterns)


def discover(roots, extensions=None, excludes=()):
    found = {}
    for raw in roots:
        root = regular(raw)
        if not root.exists():
            raise ValueError("input does not exist: " + str(root))
        if root.is_file():
            candidates = [(root, Path(root.name))]
        elif root.is_dir():
            candidates = []

            def walk_error(error):
                raise error

            for parent, dirs, names in os.walk(
                root, onerror=walk_error, followlinks=False
            ):
                dirs[:] = sorted(d for d in dirs if not (Path(parent) / d).is_symlink())
                for name in sorted(names):
                    p = Path(parent) / name
                    if p.is_file() and not p.is_symlink():
                        candidates.append((p, p.relative_to(root)))
        else:
            raise ValueError("input is not a regular file or directory: " + str(root))
        for p, rel in candidates:
            if excluded(rel.as_posix(), excludes):
                continue
            if extensions is None or any(
                p.name.lower().endswith(e) for e in extensions
            ):
                found.setdefault(p, rel)
    return sorted(found.items(), key=lambda item: os.fsencode(item[0]))


def publish(destination, writer, verifier):
    destination = regular(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        raise FileExistsError("output already exists: " + str(destination))
    with tempfile.TemporaryDirectory(
        prefix=".utility-", dir=destination.parent
    ) as folder:
        temp = Path(folder) / ("output" + "".join(destination.suffixes))
        writer(temp)
        if not temp.is_file():
            raise RuntimeError("operation produced no output")
        verifier(temp)
        with temp.open("rb") as stream:
            os.fsync(stream.fileno())
        # link() fails atomically if another worker/process created this destination.
        os.link(temp, destination)


def write_json(path, data):
    publish(
        path,
        lambda p: p.write_text(json.dumps(data, ensure_ascii=True, indent=2) + "\n"),
        lambda p: json.loads(p.read_text()),
    )


def parser(tool):
    p = argparse.ArgumentParser(
        prog=tool["name"],
        description=tool["description"],
        epilog="Writes require --apply. Sources are retained. Existing outputs are never overwritten. Exit: 0 success, 1 failure, 2 usage/dependency.",
    )
    p.add_argument(
        "paths",
        nargs="*",
        help="files or recursively scanned directories; use -- before leading dashes",
    )
    p.add_argument(
        "--exclude",
        action="append",
        default=[],
        metavar="GLOB",
        help="exclude relative file paths matching a case-sensitive glob; repeatable",
    )
    p.add_argument(
        "--config",
        type=Path,
        help="JSON config, defaults to XDG_CONFIG_HOME/" + SUITE + "/config.json",
    )
    p.add_argument(
        "--apply", action="store_true", help="execute output-producing operations"
    )
    p.add_argument("-n", "--dry-run", action="store_true", help="plan without writes")
    p.add_argument("-j", "--jobs", type=int, help="parallel workers, 1 to 32")
    p.add_argument(
        "-q", "--quiet", action="store_true", help="suppress progress on stderr"
    )
    p.add_argument("-o", "--output", type=Path, help="explicit output for one input")
    p.add_argument(
        "--output-dir", type=Path, help="batch output tree preserving relative paths"
    )
    p.add_argument("--against", type=Path, help="comparison tree or reference image")
    p.add_argument(
        "--manifest", type=Path, help="JSON SHA-256 manifest for hash-verify"
    )
    p.add_argument("-S", "--success-log", type=Path, help="new JSON success report")
    p.add_argument("-L", "--failure-log", type=Path, help="new JSON failure report")
    p.add_argument(
        "--size", default="1280x1280", help="image bounding box WIDTHxHEIGHT"
    )
    p.add_argument("--quality", type=int, default=85, help="image quality 1 to 100")
    p.add_argument("--start", type=float, default=0, help="video start time in seconds")
    p.add_argument(
        "--duration", type=float, default=10, help="video clip duration in seconds"
    )
    p.add_argument(
        "--max-bytes",
        type=int,
        default=10 * 1024**3,
        help="archive uncompressed-byte limit",
    )
    p.add_argument(
        "--max-members", type=int, default=100000, help="archive member-count limit"
    )
    return p


def load_args(tool, argv):
    p = parser(tool)
    args = p.parse_args(argv)
    if any(not pattern for pattern in args.exclude):
        p.error("--exclude patterns must not be empty")
    if args.exclude and tool["operation"] == "pack":
        p.error("--exclude is not supported for folder packing")
    config_path = (
        args.config
        or Path(os.environ.get("XDG_CONFIG_HOME", str(Path.home() / ".config")))
        / SUITE
        / "config.json"
    )
    config = {}
    if args.config or config_path.exists() or config_path.is_symlink():
        try:
            config = json.loads(regular(config_path).read_text())
            if not isinstance(config, dict) or set(config) - {"roots", "jobs"}:
                raise ValueError("only roots and jobs are supported")
            if not isinstance(config.get("roots", []), list) or not all(
                isinstance(x, str) for x in config.get("roots", [])
            ):
                raise ValueError("roots must be an array of paths")
        except (ValueError, OSError) as error:
            p.error("invalid config: " + str(error))
    args.paths = args.paths or config.get("roots", [])
    args.jobs = args.jobs if args.jobs is not None else config.get("jobs", 1)
    if type(args.jobs) is not int or not 1 <= args.jobs <= 32:
        p.error("--jobs must be 1 to 32")
    if (
        not 1 <= args.quality <= 100
        or args.start < 0
        or args.duration <= 0
        or args.max_bytes <= 0
        or args.max_members <= 0
    ):
        p.error("quality, time, and archive limits are outside their allowed ranges")
    import re, math

    if not re.fullmatch(r"[1-9][0-9]{0,4}x[1-9][0-9]{0,4}", args.size):
        p.error("--size must be WIDTHxHEIGHT, each dimension 1 to 99999")
    if not math.isfinite(args.start) or not math.isfinite(args.duration):
        p.error("times must be finite")
    if not args.paths:
        p.error("provide input paths or configure roots")
    if args.output and args.output_dir:
        p.error("--output and --output-dir are mutually exclusive")
    if tool["mode"] == "write" and not (args.output or args.output_dir):
        p.error("provide --output or --output-dir")
    if tool["mode"] == "read" and (args.output or args.output_dir or args.apply):
        p.error("read-only tools print JSON to stdout and reject output/apply options")
    if tool["operation"] in ("tree-diff", "compare") and not args.against:
        p.error("--against is required")
    if tool["operation"] == "hash-verify" and not args.manifest:
        p.error("--manifest is required")
    return args


def manifest_entries(path):
    """Accept a saved CLI response or the original bare manifest array."""
    data = json.loads(regular(path).read_text())
    if isinstance(data, dict):
        if data.get("tool") != "hash-manifest" or data.get("failures") != []:
            raise ValueError("manifest must be a successful hash-manifest response")
        data = data.get("results")
    if not isinstance(data, list):
        raise ValueError("manifest must contain an array of entries")
    seen = set()
    for entry in data:
        if not isinstance(entry, dict):
            raise ValueError("manifest entries must be objects")
        name, checksum = entry.get("path"), entry.get("sha256")
        if (
            not isinstance(name, str)
            or not name
            or "\x00" in name
            or any(part in ("", ".", "..") for part in name.split("/"))
        ):
            raise ValueError("manifest paths must be unambiguous relative file paths")
        if name in seen:
            raise ValueError("ambiguous duplicate relative paths in manifest")
        seen.add(name)
        if not isinstance(checksum, str) or not re.fullmatch(
            r"[0-9a-fA-F]{64}", checksum
        ):
            raise ValueError("manifest SHA-256 must contain 64 hexadecimal characters")
        if "bytes" in entry and (type(entry["bytes"]) is not int or entry["bytes"] < 0):
            raise ValueError("manifest bytes must be a nonnegative integer")
    return {entry["path"]: entry["sha256"].lower() for entry in data}


def ordered_work(pool, function, items, limit):
    """Keep at most limit futures outstanding while preserving input order."""
    items = iter(items)
    pending = deque()
    try:
        for _ in range(limit):
            item = next(items, None)
            if item is None:
                break
            pending.append(pool.submit(function, item))
        while pending:
            yield pending.popleft().result()
            item = next(items, None)
            if item is not None:
                pending.append(pool.submit(function, item))
    finally:
        for future in pending:
            future.cancel()


def common(tool, files, args):
    op = tool["operation"]
    if op == "inventory":
        return [
            {"path": str(p), "relative": str(rel), "bytes": p.stat().st_size}
            for p, rel in files
        ]
    if op == "summary":
        extensions = {}
        total_bytes = empty_files = 0
        smallest = largest = None
        for path, _ in files:
            size = path.stat().st_size
            total_bytes += size
            empty_files += int(size == 0)
            smallest = size if smallest is None else min(smallest, size)
            largest = size if largest is None else max(largest, size)
            extension = path.suffix.lower()
            if extension == ".":
                extension = ""  # Keep trailing-dot names consistent on Python 3.11+.
            group = extensions.setdefault(
                extension, {"extension": extension, "file_count": 0, "total_bytes": 0}
            )
            group["file_count"] += 1
            group["total_bytes"] += size
        return [
            {
                "file_count": len(files),
                "total_bytes": total_bytes,
                "empty_files": empty_files,
                "min_bytes": smallest,
                "max_bytes": largest,
                "extensions": [extensions[key] for key in sorted(extensions)],
            }
        ]
    if op == "duplicates":
        sizes = {p: p.stat().st_size for p, _ in files}
        counts = Counter(sizes.values())
        groups = {}
        for p, _ in files:
            if counts[sizes[p]] > 1:
                groups.setdefault(digest(p), []).append(str(p))
        return [{"sha256": h, "paths": ps} for h, ps in groups.items() if len(ps) > 1]
    if op == "manifest":
        if len({str(rel) for _, rel in files}) != len(files):
            raise ValueError("ambiguous duplicate relative paths")
        return [
            {"path": str(rel), "sha256": digest(p), "bytes": p.stat().st_size}
            for p, rel in files
        ]
    if op == "hash-verify":
        expected = {
            name: checksum
            for name, checksum in manifest_entries(args.manifest).items()
            if not excluded(name, args.exclude)
        }
        if len({str(rel) for _, rel in files}) != len(files):
            raise ValueError("ambiguous duplicate relative paths")
        actual = {str(rel): digest(p) for p, rel in files}
        result = [
            {"path": name, "ok": expected.get(name) == actual.get(name)}
            for name in sorted(expected.keys() | actual.keys())
        ]
        if any(not row["ok"] for row in result):
            raise ValueError("manifest mismatch: " + json.dumps(result))
        return result
    if op == "tree-diff":
        left = {str(rel): digest(p) for p, rel in files}
        right = {
            str(rel): digest(p)
            for p, rel in discover([args.against], excludes=args.exclude)
        }
        if len(left) != len(files):
            raise ValueError("ambiguous duplicate relative paths")
        return [
            {
                "path": name,
                "status": "right-only"
                if name not in left
                else "left-only"
                if name not in right
                else "changed",
            }
            for name in sorted(left.keys() | right.keys())
            if left.get(name) != right.get(name)
        ]
    if op == "path-audit":
        return [
            {"path": str(p), "issues": issues}
            for p, rel in files
            if (
                issues := [
                    name
                    for name, bad in [
                        ("control character", any(ord(c) < 32 for c in str(rel))),
                        (
                            "Windows reserved character",
                            any(c in '<>:"\\|?*' for c in str(rel)),
                        ),
                        (
                            "long component",
                            any(len(os.fsencode(c)) > 240 for c in rel.parts),
                        ),
                        (
                            "trailing dot or space",
                            any(c.endswith((".", " ")) for c in rel.parts),
                        ),
                    ]
                    if bad
                ]
            )
        ]
    return None


def execute(tool, args):
    import domain

    if tool["operation"] == "pack":
        files = [(regular(p), Path(regular(p).name)) for p in args.paths]
        if any(not p.is_dir() for p, _ in files):
            raise UsageError("pack requires directory inputs")
    else:
        files = discover(args.paths, tool.get("extensions"), args.exclude)
    if not files:
        raise ValueError("no matching input files")
    aggregate = common(tool, files, args)
    if aggregate is not None:
        return aggregate, []
    if args.output and len(files) != 1:
        raise UsageError("--output requires exactly one input")
    targets = []
    if tool["mode"] == "write":
        for source, rel in files:
            target = args.output or args.output_dir / (str(rel) + "." + tool["suffix"])
            target = regular(target)
            if any(
                target == p or (p.is_dir() and target.is_relative_to(p))
                for p, _ in files
            ):
                raise UsageError("output must be outside source inputs")
            if target.exists():
                raise FileExistsError("output already exists: " + str(target))
            targets.append(target)
        if len(set(targets)) != len(targets):
            raise UsageError("multiple inputs map to the same output")

    def one(index):
        source, _ = files[index]
        record = {"path": str(source), "tool": tool["name"]}
        try:
            if tool["mode"] == "write":
                record["output"] = str(targets[index])
                if args.dry_run or not args.apply:
                    record["status"] = "planned"
                else:
                    domain.write(tool, source, targets[index], args)
                    record["status"] = "written"
            else:
                record["result"] = domain.inspect(tool, source, args)
                record["status"] = "ok"
        except Exception as error:
            record.update(
                status="failed",
                error=str(error),
                dependency=isinstance(error, UsageError),
            )
        return record

    records = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.jobs) as pool:
        for index, record in enumerate(
            ordered_work(pool, one, range(len(files)), 2 * args.jobs)
        ):
            records.append(record)
            if not args.quiet:
                print(
                    f"[{index + 1}/{len(files)}] {record['status']} {json.dumps(record['path'])}",
                    file=sys.stderr,
                )
    return [r for r in records if r["status"] != "failed"], [
        r for r in records if r["status"] == "failed"
    ]


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    tools = catalog()
    if not argv or argv[0] in ("-h", "--help", "list"):
        print(
            SUITE
            + " - offline batch utilities\nUsage: bin/"
            + SUITE
            + " TOOL [options] PATH...\n"
        )
        for tool in tools:
            print(tool["name"] + "  " + tool["description"])
        return 0
    if argv[0] == "--version":
        print((ROOT / "VERSION").read_text().strip())
        return 0
    tool = next((t for t in tools if t["name"] == argv[0]), None)
    if tool is None:
        print("unknown tool: " + argv[0], file=sys.stderr)
        return 2
    try:
        args = load_args(tool, argv[1:])
        for report in (args.success_log, args.failure_log):
            if report and (regular(report).exists()):
                raise UsageError("report already exists: " + str(report))
        good, bad = execute(tool, args)
        if not args.dry_run:
            if args.success_log:
                write_json(args.success_log, good)
            if args.failure_log:
                write_json(args.failure_log, bad)
        print(
            json.dumps(
                {"tool": tool["name"], "results": good, "failures": bad},
                ensure_ascii=True,
                indent=2,
            )
        )
        return 2 if any(r.get("dependency") for r in bad) else int(bool(bad))
    except UsageError as error:
        print("ERROR: " + str(error), file=sys.stderr)
        return 2
    except (
        OSError,
        ValueError,
        RuntimeError,
        KeyError,
        TypeError,
        subprocess.TimeoutExpired,
    ) as error:
        print("FAIL: " + str(error), file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("Interrupted", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
