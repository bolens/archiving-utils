# Archive preservation utilities constitution

## Core principles

### I. Domain verification

ZIP, TAR, gzip, bz2, and lzma operations use Python standard-library codecs. Reject unsafe archive members, links, duplicate destinations, excessive expansion, and corrupt output before publication.

### II. Preserve sources and destinations

Source files MUST remain intact. Writes require `--apply`, verified temporary
outputs, and no-clobber publication. Reject input symlinks and destination
collisions. Preserve filename bytes through argument arrays; never use shell
evaluation for filenames.

### III. One catalog and shared engine

`lib/catalog.json` owns tool identity and generated surfaces. Thin Bash wrappers
call the shared Python engine; domain behavior belongs in `lib/domain.py`.
Imports MUST have no operational side effects. Keep Python 3.11 compatibility.

### IV. Explicit local authority

Commands are offline and MUST NOT install packages, delete sources, or access a
personal library during tests. MCP is local stdio, read-only, and limited to
configured roots. Do not broaden its authority without a reviewed contract.

### V. Executable evidence

Use disposable fixtures and isolated HOME/XDG/TMPDIR values. Preserve exit codes
0 success, 1 operation failure, and 2 usage/dependency failure. Run
`make check test-all` before publication and report every dependency skip.

## Governance

Read `AGENTS.md`, `docs/architecture.md`, `docs/requirements.md`, and
`tests/README.md`. Safety or compatibility exceptions need explicit rationale,
acceptance evidence, and a constitution version update.

**Version**: 1.0.0 | **Ratified**: 2026-09-05 | **Last Amended**: 2026-09-05
