# Plan: Archive preservation and local library tools

The [specification](spec.md) preserves existing behavior. Use the project guide
and constitution for implementation constraints. Keep upstream-managed templates,
helpers, and integration manifests unchanged.

## Source ownership

- `lib/core.py`
- `lib/domain.py`
- `lib/catalog.json`
- `mcp/server.py`
- `scripts/generate.py`
- `tests/test_common.py`
- `tests/test_functional.py`
- `docs/formats.md`

## Constitution check

Preserve explicit local write authority, source retention, no-clobber publication, Python 3.11 compatibility, and the catalog/shared-engine boundary. The retrofit changes documentation only and introduces no codec, protocol, media write, or live service.

## Validation

```sh
make check test-all
```

Run checks in an isolated checkout. Commands are instructions, not evidence of
a pass. Record results in `coverage.md`, keep incomplete work in `tasks.md`, and
follow `RELEASING.md` for reviewed delivery. No live operation is required solely
to create this retrospective baseline.

## Legacy completion audit, 2026-09-06

Inventory all 48 catalog entries and supporting CLI/configuration, MCP, generated
site, development and delivery surfaces. Extend this baseline with concrete
contracts for the 31 original archive/library commands while retaining spec 001
for the 17 comic commands. Trace shared planning/publication and domain operations
to native fixtures. Preserve the catalog-generated references as normative
single sources; no generated output changes are required for this documentation
retrofit. Verify source/fixture mapping, native checks, and protected delivery.
