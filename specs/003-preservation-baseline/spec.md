# Feature specification: Archive preservation and local library tools

**Created**: 2026-09-05
**Status**: Retrospective baseline
**Inspected revision**: `061aadf1036f32bb2da254c12164565a055a75e2`
**Input**: The owner requested a fleet-wide Spec Kit retrofit and implementation audit.

Standard-library codecs package, repack, inspect, and extract archives; the existing comic specification adds optional native formats.

This specification records existing contracts after implementation. It does not
claim that the original work followed Spec Kit. New behavior requires a separate
change contract. Existing feature specifications remain authoritative within their
own scope.

## User scenarios and testing

### User story 1: Plan a conversion before writing (P1)

An operator selects local files and a catalog command.

**Acceptance**: Without --apply, the command reports planned destinations and leaves sources and outputs unchanged.

### User story 2: Publish verified outputs while retaining sources (P2)

An operator explicitly applies a conversion using disposable fixtures.

**Acceptance**: A valid conversion is verified before no-clobber publication. Corruption, unsupported operations, and collisions produce nonzero status without publishing failed output.

### User story 3: Inspect a collection through CLI or restricted MCP (P3)

An operator inventories files, computes manifests, compares trees, or requests a permitted read-only MCP operation.

**Acceptance**: Summaries do not read media contents, hashes round-trip through verification, and MCP refuses paths outside its configured roots and all write commands.

## Requirements

- **FR-001**: The catalog MUST own tool names, operation selection, wrappers, and generated documentation.
- **FR-002**: Writes MUST require --apply, retain source bytes, refuse existing destinations, and verify staged output before publication.
- **FR-003**: Discovery MUST preserve unusual filenames, reject input symlinks, apply explicit exclusions before work, and reject ambiguous destinations.
- **FR-004**: Archive operations MUST reject unsafe member paths, links, duplicate destinations, corrupt content, and expansion limits before publishing output.
- **FR-005**: Shared library tools MUST provide inventory, summary, exact duplicate hashes, manifests, hash verification, tree comparison, and path auditing without deleting source files.
- **FR-006**: MCP MUST remain local stdio, expose only read operations, require allowed roots, and reject unknown arguments.
- **FR-007**: Batch execution MUST bound outstanding jobs, preserve result ordering, retain successful outputs, and report partial failures with nonzero exit status.

## Success criteria

- **SC-001**: Every requirement has a named source owner and acceptance check in `coverage.md`.
- **SC-002**: The listed native checks pass for the reviewed candidate, with unavailable environments and operational checks recorded separately.
- **SC-003**: Retrofitting preserves existing interfaces and completed specifications. Any confirmed implementation gap is corrected under an explicit requirement before it is marked complete.

## Edge cases and operational limits

Validation uses disposable fixtures. No personal library or live service is involved. Native codec support is bounded by docs/requirements.md and docs/formats.md. Comic container metadata limits remain governed by specs/001-comic-archives/spec.md. Docker runtime and hosted delivery retain their existing separate checks. Source delivery does not authorize a new version tag.
