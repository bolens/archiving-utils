#!/usr/bin/env python3
"""Generate thin commands, per-tool references, catalog tables, and the static site."""

import argparse
import html
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "lib"))
import core

DETAILS = {
    "archiving-utils": dict(
        label="ARCHIVE / FIELD INDEX",
        title="Keep the files.\nProve the contents.",
        intro="Package, inspect, compare, and recover local archives. Every compression pipeline checks the round trip before publishing its output.",
        feature="folder-to-tar-xz",
        example="bin/archiving-utils folder-to-tar-xz --output collection.tar.xz --apply ./collection",
        formats="ZIP · TAR · GZIP · BZIP2 · XZ",
        section="The archive cabinet",
        art="archive",
    ),
    "image-utils": dict(
        label="IMAGE / WORKING COLLECTION",
        title="A considered toolkit\nfor every frame.",
        intro="Convert raster formats, prepare previews, inspect metadata, and check image libraries from the command line. Your originals stay where they are.",
        feature="image-thumbnail",
        example="bin/image-utils image-thumbnail --size 640x640 --output-dir ./previews --apply ./originals",
        formats="PNG · JPEG · WEBP · TIFF · AVIF · HEIC · JXL",
        section="Find the right instrument",
        art="image",
    ),
    "video-utils": dict(
        label="VIDEO / LOCAL OPERATIONS",
        title="From source reel\nto verified output.",
        intro="Remux containers, encode viewing copies, inspect streams, and find picture or audio faults. Batch operations for the life of a video library.",
        feature="video-to-h264",
        example="bin/video-utils video-to-h264 --output-dir ./viewing --apply ./masters",
        formats="MATROSKA · MP4 · WEBM · FFV1 · H.264 · HEVC",
        section="Choose an operation",
        art="video",
    ),
}


def generate():
    suite = ROOT.name
    d = DETAILS[suite]
    files = {}
    tools = core.catalog()
    for tool in tools:
        name = tool["name"]
        folder = (
            Path("conversion") / name
            if tool["category"] == "conversion"
            else Path("util") / tool["category"] / name
        )
        up = "../.." if tool["category"] == "conversion" else "../../.."
        files[folder / (name + ".sh")] = (
            f'#!/usr/bin/env bash\nset -euo pipefail\nroot=$(cd -- "$(dirname -- "${{BASH_SOURCE[0]}}")/{up}" && pwd)\nexec "$root/bin/{suite}" {name} "$@"\n'
        )
        files[folder / "Makefile"] = (
            f"ROOT := $(abspath {up})\nTOOL := {name}\ninclude $(ROOT)/lib/tool.mk\n"
        )
        files[folder / "README.md"] = (
            f"# {name}\n\n{tool['description']}\n\nMode: **{tool['mode']}**. Operation: `{tool['operation']}`.\n\n"
            + (
                "Source extensions: "
                + ", ".join("`" + e + "`" for e in tool["extensions"])
                + ".\n\n"
                if tool.get("extensions")
                else ""
            )
            + f"Run from the repository root:\n\n```bash\nbin/{suite} {name} --help\n```\n\n"
            + (
                "Writes require `--apply` and `--output` or `--output-dir`. Without `--apply`, this command prints a plan. Existing destinations are refused and source files are retained.\n\n"
                if tool["mode"] == "write"
                else "Prints JSON to stdout. Does not modify inputs.\n\n"
            )
            + f"[CLI contract]({up}/docs/cli.md) · [Formats and limits]({up}/docs/formats.md)\n\n```text\n{core.parser(tool).format_help()}```\n"
        )
    rows = "\n".join(
        f"| [`{t['name']}`](../{'conversion/' + t['name'] if t['category'] == 'conversion' else 'util/' + t['category'] + '/' + t['name']}/) | {t['category']} | {t['mode']} | {t['description']} |"
        for t in tools
    )
    files[Path("docs/catalog.md")] = (
        f"# Tool catalog\n\n{len(tools)} commands. Generated from `lib/catalog.json`.\n\n| Command | Category | Mode | Purpose |\n|---|---|---|---|\n{rows}\n"
    )
    files[Path("README.md")] = f"""# {suite}

[![CI](https://github.com/bolens/{suite}/actions/workflows/ci.yml/badge.svg)](https://github.com/bolens/{suite}/actions/workflows/ci.yml)

{d["intro"]}

**[Browse the site](https://bolens.github.io/{suite}/)** · [Command catalog](docs/catalog.md) · [Architecture diagram](https://bolens.github.io/{suite}/diagrams/architecture.html)

## Start here

GNU/Linux, Bash 4.3+, and Python 3.11+. See [requirements](docs/requirements.md) for operation-specific dependencies.

```bash
git clone https://github.com/bolens/{suite}.git
cd {suite}
bin/{suite} list
{d["example"].replace(" --apply", "")}
# Review the plan, then add --apply to create outputs.
```

{len(tools)} commands cover conversion, inspection, and library maintenance. Tool directories are thin Bash entry points over a shared Python engine, following the layout and preservation intent of [audio-utils](https://github.com/bolens/audio-utils).

## Working contract

- Writes require `--apply`. `--dry-run` suppresses writes, including report files.
- Sources are retained. Outputs are verified in a temporary directory and published without overwriting existing destinations.
- Inputs can be files or recursive directory trees. Input symlinks are not followed. Filenames travel as arguments, never shell code.
- JSON results go to stdout. Progress and failures go to stderr. Exit codes are 0 success, 1 operation failure, 2 usage or dependency failure.
- `-j 1..32` controls batch concurrency. `--output-dir` preserves relative paths and appends the output suffix to the complete source name.
- The stdio MCP server exposes only read-only tools under explicitly allowed roots.

## Development

```bash
make check
make test
make test-functional
make test-all
make generate
make install-hooks
make -C {"conversion/" + d["feature"] if d["feature"] in [t["name"] for t in tools if t["category"] == "conversion"] else "util/transform/" + d["feature"]} help
```

[CLI and configuration](docs/cli.md) · [Formats and limits](docs/formats.md) · [Architecture](docs/architecture.md) · [MCP](docs/mcp.md) · [Tests](tests/README.md) · [Release procedure](docs/releasing.md) · [Contributing](CONTRIBUTING.md)

## Status

Initial 0.1.0 implementation. This is a sibling suite, not a claim of identical feature maturity or codec coverage to audio-utils. The [parity notes](docs/parity.md) explain the implemented conventions and deliberate differences.

[MIT license](LICENSE). External encoders keep their own licenses.
"""
    category_options = "".join(
        f'<option value="{c}">{c.capitalize()}</option>'
        for c in sorted({t["category"] for t in tools})
    )
    cards = "".join(
        f'''<article class="tool" data-category="{t["category"]}" data-search="{html.escape(t["name"] + " " + t["description"], quote=True)}"><div class="tool-meta"><span>{t["category"]}</span><span>{"Creates a copy" if t["mode"] == "write" else "Read only"}</span></div><h3><a href="https://github.com/bolens/{suite}/tree/main/{"conversion/" + t["name"] if t["category"] == "conversion" else "util/" + t["category"] + "/" + t["name"]}">{t["name"]}</a></h3><p>{html.escape(t["description"])}</p><code>{"--apply to write" if t["mode"] == "write" else "JSON to stdout"}</code></article>'''
        for t in tools
    )
    art = {
        "archive": '<div class="cabinet"><div class="drawer"><span>01 / PACKAGE</span><b>collection.tar.xz</b><small>MEMBER CHECKSUMS</small></div><div class="drawer"><span>02 / INSPECT</span><b>archive-manifest</b><small>SHA-256 / JSON</small></div><div class="drawer"><span>03 / RECOVER</span><b>archive-extract</b><small>NEW DIRECTORY ONLY</small></div></div>',
        "image": '<div class="contact-art"><div class="swatch s1"><span>ORIGINAL</span></div><div class="swatch s2"><span>GRAYSCALE</span></div><div class="swatch s3"><span>CROP</span></div><div class="swatch s4"><span>THUMBNAIL</span></div></div><p class="art-note">A study in shape. Four ways to prepare a frame.</p>',
        "video": '<div class="monitor"><div class="timecode">00:00:12:00 <span>LOCAL SOURCE</span></div><div class="frame-art"><i></i><i></i><i></i><i></i></div><div class="tracks"><div><span>V1</span><b>PICTURE / COPY OR ENCODE</b></div><div><span>A1</span><b>AUDIO / DECODE CHECK</b></div><div><span>OUT</span><b>VERIFY → PUBLISH</b></div></div></div>',
    }[d["art"]]
    files[Path("site/index.html")] = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="description" content="{html.escape(d["intro"])}"><meta name="color-scheme" content="light dark"><title>{suite} — local library tools</title><link rel="icon" href="favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="style.css"><script src="app.js" defer></script></head>
<body class="{d["art"]}"><a class="skip" href="#main">Skip to content</a><header><a class="wordmark" href="./">{suite}</a><nav aria-label="Main"><a href="#catalog">Tools</a><a href="diagrams/architecture.html">Architecture</a><a href="https://github.com/bolens/{suite}">GitHub ↗</a><button id="theme" type="button" aria-label="Toggle color theme">Theme</button></nav></header>
<main id="main"><section class="hero"><div class="hero-copy"><p class="eyebrow">{d["label"]}</p><h1>{html.escape(d["title"]).replace(chr(10), "<br>")}</h1><p class="intro">{d["intro"]}</p><div class="hero-actions"><a class="primary" href="#start">Start with a plan <span>↗</span></a><a href="#catalog">Explore {len(tools)} commands ↓</a></div></div><div class="hero-art" aria-hidden="true">{art}</div></section>
<div class="format-band"><span>FORMAT DESK</span><p>{d["formats"]}</p></div>
<section id="start" class="start"><div><p class="eyebrow">WORK LOCALLY</p><h2>Inspect first.<br>Write deliberately.</h2><p>Clone the repository and install the <a href="https://github.com/bolens/{suite}/blob/main/docs/requirements.md">required tools</a>. Run this command to preview the work. Add <code>--apply</code> when the plan is right.</p></div><div class="terminal"><div class="terminal-title"><span>TERMINAL / PREVIEW</span><button id="copy" type="button">Copy command</button></div><pre><code id="command">{html.escape(d["example"].replace(" --apply", ""))}</code></pre><p id="copy-status" role="status">Sources retained · Existing outputs refused</p></div></section>
<section id="catalog" class="catalog"><div class="section-heading"><div><p class="eyebrow">THE TOOL INDEX</p><h2>{d["section"]}</h2></div><p id="count" role="status">{len(tools)} commands</p></div><div class="filters"><label>Search commands<input type="search" id="search" placeholder="Try verify, metadata, convert…"></label><label>Category<select id="category"><option value="all">All categories</option>{category_options}</select></label></div><div class="tools">{cards}</div><p id="empty" hidden>No commands match. Try another search or select all categories.</p></section>
<section class="architecture-link"><div><p class="eyebrow">UNDER THE SURFACE</p><h2>Follow a file through the system.</h2><p>Explore the shared driver, domain operations, verification, and output publication in the interactive architecture diagram.</p></div><a class="primary" href="diagrams/architecture.html">Open architecture <span>↗</span></a></section>
</main><footer><a class="wordmark" href="./">{suite}</a><p>GNU/Linux · Offline CLI · MIT</p><div>{"".join(f'<a href="https://bolens.github.io/{s}-utils/">{s}</a>' for s in ("archiving", "image", "video") if s + "-utils" != suite)}<a href="https://github.com/bolens/audio-utils">audio</a></div></footer></body></html>\n'''
    files[Path("site/.nojekyll")] = ""
    return files


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--check", action="store_true")
    args = p.parse_args()
    mismatches = []
    for relative, content in generate().items():
        target = ROOT / relative
        if args.check:
            if not target.exists() or target.read_text() != content:
                mismatches.append(str(relative))
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content)
            if target.suffix == ".sh":
                target.chmod(0o755)
    if mismatches:
        sys.exit("Generated files are stale: " + ", ".join(mismatches))
