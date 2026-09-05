#!/usr/bin/env python3
"""Read-only stdio MCP endpoint. Explicit local roots are mandatory."""

import argparse
import contextlib
import io
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))
import core

MAX_LINE = 1024 * 1024


def serve(roots):
    allowed = [core.regular(p) for p in roots]
    if not all(p.is_dir() for p in allowed):
        raise ValueError("allowed roots must be existing directories")
    tools = [
        t
        for t in core.catalog()
        if t["mode"] == "read"
        and t["operation"] not in ("hash-verify", "tree-diff", "compare")
    ]
    ready = False
    while True:
        line = sys.stdin.buffer.readline(MAX_LINE + 1)
        if not line:
            return
        if len(line) > MAX_LINE:
            return
        ident = None
        try:
            request = json.loads(line)
            if (
                not isinstance(request, dict)
                or request.get("jsonrpc") != "2.0"
                or not isinstance(request.get("method"), str)
            ):
                raise ValueError("invalid JSON-RPC request")
            ident = request.get("id")
            method = request["method"]
            if "id" not in request:
                continue
            params = request.get("params", {})
            if not isinstance(params, dict):
                raise ValueError("params must be an object")
            if method == "initialize":
                version = params.get("protocolVersion")
                if version not in (
                    "2024-11-05",
                    "2025-03-26",
                    "2025-06-18",
                    "2025-11-25",
                ):
                    version = "2025-11-25"
                ready = True
                result = {
                    "protocolVersion": version,
                    "capabilities": {"tools": {"listChanged": False}},
                    "serverInfo": {
                        "name": core.SUITE,
                        "version": (core.ROOT / "VERSION").read_text().strip(),
                    },
                }
            elif method == "ping":
                result = {}
            elif not ready:
                raise ValueError("initialize first")
            elif method == "tools/list":
                result = {
                    "tools": [
                        {
                            "name": t["name"],
                            "description": t["description"],
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "paths": {
                                        "type": "array",
                                        "items": {"type": "string"},
                                        "minItems": 1,
                                        "maxItems": 100,
                                    }
                                },
                                "required": ["paths"],
                                "additionalProperties": False,
                            },
                            "annotations": {
                                "readOnlyHint": True,
                                "destructiveHint": False,
                                "openWorldHint": False,
                            },
                        }
                        for t in tools
                    ]
                }
            elif method == "tools/call":
                try:
                    tool = next(
                        (t for t in tools if t["name"] == params.get("name")), None
                    )
                    if tool is None:
                        raise ValueError("unknown read-only tool")
                    arguments = params.get("arguments", {})
                    if not isinstance(arguments, dict) or set(arguments) != {"paths"}:
                        raise ValueError("only paths is accepted")
                    paths = arguments["paths"]
                    if (
                        not isinstance(paths, list)
                        or not 1 <= len(paths) <= 100
                        or not all(isinstance(p, str) for p in paths)
                    ):
                        raise ValueError("paths must contain 1 to 100 strings")
                    resolved = [core.regular(p) for p in paths]
                    if not all(
                        any(p.is_relative_to(root) for root in allowed)
                        for p in resolved
                    ):
                        raise ValueError("path outside allowed roots")
                    # No user config, report paths, writes, or arbitrary CLI switches.
                    args = core.parser(tool).parse_args(
                        ["--quiet", "--jobs", "1", "--", *map(str, resolved)]
                    )
                    args.jobs = 1
                    with contextlib.redirect_stdout(io.StringIO()):
                        good, bad = core.execute(tool, args)
                    body = json.dumps(
                        {"results": good, "failures": bad}, ensure_ascii=True
                    )
                    if len(body) > 4 * 1024 * 1024:
                        raise ValueError(
                            "result exceeds 4 MiB; use a smaller input tree"
                        )
                    result = {
                        "content": [{"type": "text", "text": body}],
                        "isError": bool(bad),
                    }
                except Exception as error:
                    result = {
                        "content": [{"type": "text", "text": str(error)}],
                        "isError": True,
                    }
            else:
                print(
                    json.dumps(
                        {
                            "jsonrpc": "2.0",
                            "id": ident,
                            "error": {"code": -32601, "message": "Method not found"},
                        }
                    ),
                    flush=True,
                )
                continue
            response = {"jsonrpc": "2.0", "id": ident, "result": result}
        except json.JSONDecodeError:
            response = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32700, "message": "Parse error"},
            }
        except (ValueError, TypeError, KeyError) as error:
            response = {
                "jsonrpc": "2.0",
                "id": ident,
                "error": {"code": -32600, "message": str(error)},
            }
        print(json.dumps(response, ensure_ascii=True), flush=True)


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--allow-root", action="append", required=True)
    args = p.parse_args()
    serve(args.allow_root)
