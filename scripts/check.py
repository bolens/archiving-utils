#!/usr/bin/env python3
"""Check Python syntax, Bash wrappers, generated docs, local links, and action pins."""

import ast
from pathlib import Path
import re
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def main():
    for path in ROOT.rglob("*.py"):
        ast.parse(path.read_text(), filename=str(path))
    scripts = sorted(ROOT.rglob("*.sh")) + [
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
