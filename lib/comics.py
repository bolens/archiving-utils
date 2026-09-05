"""Comic page inventory without decoding images or rewriting sidecars."""

from pathlib import PurePosixPath
import re

PAGE_EXTENSIONS = frozenset((
    ".jpg", ".jpeg", ".jpe", ".jfif", ".png", ".apng", ".webp", ".gif",
    ".tif", ".tiff", ".bmp", ".dib", ".avif", ".heic", ".heif", ".jxl",
    ".jp2", ".j2k", ".jpf", ".jpx", ".ppm", ".pgm", ".pbm", ".pnm", ".qoi",
))


def natural_key(name):
    # ASCII digits only; the original name breaks case/zero-padding ties.
    return (tuple((1, int(part)) if part.isascii() and part.isdigit() else (0, part)
                  for part in re.split(r"([0-9]+)", name.casefold())), name)


def inventory(rows):
    files = [row for row in rows if not row["directory"]]
    pages = sorted((row for row in files
                    if PurePosixPath(row["name"]).suffix.lower() in PAGE_EXTENSIONS),
                   key=lambda row: natural_key(row["name"]))
    page_names = {row["name"] for row in pages}
    metadata = [row["name"] for row in files
                if PurePosixPath(row["name"]).name.casefold() == "comicinfo.xml"]
    return {
        "verified": True,
        "verification": "archive payload integrity; page types recognized by extension only",
        "page_count": len(pages),
        "page_order": "natural filename order; reader ordering may differ",
        "pages": pages,
        "metadata_files": metadata,
        "other_files": [row for row in files if row["name"] not in page_names],
        "members": len(rows),
        "bytes": sum(row["bytes"] for row in rows),
    }
