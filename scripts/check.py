#!/usr/bin/env python3
"""Check Python syntax, Bash wrappers, generated docs, local links, and action pins."""

import ast
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def managed_spec_kit_files():
    """Verify upstream-managed files before excluding them from project style checks."""
    directory = ROOT / ".specify/integrations"
    if not directory.exists():
        return set()
    manifests = sorted(directory.glob("*.manifest.json"))
    if {path.name for path in manifests} != {
        "codex.manifest.json", "speckit.manifest.json"
    }:
        sys.exit("missing Spec Kit integration manifest")
    managed = set()
    for manifest in manifests:
        files = json.loads(manifest.read_text())["files"]
        for relative, expected in files.items():
            path = Path(relative)
            if path.is_absolute() or ".." in path.parts:
                sys.exit("unsafe Spec Kit managed path")
            candidate = ROOT / path
            if (not candidate.resolve().is_relative_to(ROOT.resolve())
                    or candidate.is_symlink() or not candidate.is_file()):
                sys.exit(f"missing or symlinked managed file: {relative}")
            if hashlib.sha256(candidate.read_bytes()).hexdigest() != expected:
                sys.exit(f"Spec Kit managed hash mismatch: {relative}")
            # Never exempt project-owned files merely because a manifest lists them.
            if relative.startswith((".specify/scripts/", ".specify/templates/",
                                    ".agents/skills/speckit-")):
                managed.add(candidate)
                if candidate.suffix == ".sh":
                    subprocess.run(["bash", "-n", str(candidate)], check=True)
    return managed


def main():
    managed = managed_spec_kit_files()
    for path in ROOT.rglob("*.py"):
        ast.parse(path.read_text(), filename=str(path))
    scripts = sorted(path for path in ROOT.rglob("*.sh") if path not in managed) + [
        ROOT / "bin" / ROOT.name,
        ROOT / ".githooks/pre-commit",
    ]
    if not shutil.which("shellcheck"):
        sys.exit("missing dependency: shellcheck")
    subprocess.run(["shellcheck", "-x", *map(str, scripts)], check=True)
    subprocess.run(
        [sys.executable, str(ROOT / "scripts/generate.py"), "--check"], check=True
    )
    errors = []
    for path in ROOT.rglob("*.md"):
        if path in managed:
            continue
        for link in re.findall(r"\[[^\]]*\]\(([^)]+)\)", path.read_text()):
            if "://" in link or link.startswith(("#", "mailto:")):
                continue
            target = link.split("#")[0]
            if target and not (path.parent / target).exists():
                errors.append(f"{path.relative_to(ROOT)}: broken link {target}")
    for path in (ROOT / ".github/workflows").glob("*.yml"):
        for action in re.findall(r"uses:\s*([^\s#]+)", path.read_text()):
            if not re.fullmatch(r"[\w.-]+/[\w./-]+@[0-9a-f]{40}", action):
                errors.append("unpinned action: " + action)
    for required in (
        "site/index.html",
        "site/style.css",
        "site/app.js",
        "site/diagrams/architecture.html",
    ):
        if not (ROOT / required).exists():
            errors.append("missing " + required)
    if errors:
        sys.exit("\n".join(errors))
    print(
        "Python syntax, ShellCheck, generated files, local links, and action pins passed."
    )


if __name__ == "__main__":
    main()
