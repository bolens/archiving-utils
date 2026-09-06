# archiving-utils project guide

Archive preservation utilities for GNU/Linux, using Bash entry points and a Python 3.11+ shared engine.

## Source ownership

`bin/archiving-utils` dispatches to `lib/core.py`; domain operations belong in
`lib/domain.py`. `lib/catalog.json` owns generated wrappers, CLI reference
pages, and the site. `scripts/generate.py` owns regeneration.
`mcp/server.py` exposes the restricted read-only engine.

## Specification and acceptance decisions

Define input formats, output verification, source retention, collision
handling, resource limits, stdout/stderr, and exit codes. Keep read-only
planning distinct from explicit writes. Cover traversal and absolute archive member paths, symlinks, duplicate members, extraction limits, malformed archives, and verified compression round trips. No external archive downloader or network service is part of the tool contract.

Shared acceptance cases include spaces, newlines, leading dashes, Unicode,
symlinks, corrupt inputs, partial outputs, collision races, missing tools,
configuration errors, and MCP allowed-root enforcement. Never use personal
media as a fixture.

## Validation and delivery

Run `make check test-all`. Run `make generate` only when changing catalog or
help sources, then prove generated files are current with `make check`.
Read `docs/requirements.md` for exact runtime/delegate requirements and
`tests/README.md` for the unit and functional boundaries. CI covers Python
3.11 and 3.14. Record unavailable optional codecs/delegates honestly.

The checked site is published through the existing Pages workflow after main
CI succeeds. Firmware, live infrastructure, and personal libraries are not
validation environments. Follow `RELEASING.md` for protected squash merges.

## Spec Kit workflow

Create feature specifications for new work and explicitly requested retrospective baselines. Label retrospective scope and the inspected revision, and distinguish observed behavior from corrective requirements. Record observable acceptance
criteria in `spec.md`, source ownership and constitution checks in `plan.md`,
and executable verification in `tasks.md`. Resolve material unknowns before
implementation. Mark tasks complete only with evidence and retain completed
feature directories as decision history.

Managed templates, scripts, and Codex skills belong to their integration
manifests. Customize this guide and the constitution; do not hand-edit managed
files or hashes. Verify project-owned memory survives regeneration. The pinned
Spec Kit workflow validates integration metadata, managed hashes, constitution
metadata, and Bash syntax. Follow `RELEASING.md` for delivery.

The retrospective specification register is [specs/README.md](../../specs/README.md).
