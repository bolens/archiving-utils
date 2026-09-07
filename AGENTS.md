# Agent guidance

[Documentation](docs/README.md) maps architecture, deployment, state, and document ownership.

Use [docs/architecture.md](docs/architecture.md) for shared-engine or catalog changes,
[docs/requirements.md](docs/requirements.md) for runtime or codec requirements, and [tests/README.md](tests/README.md)
to select validation for the affected behavior. Read the relevant contract
before changing it; prose-only edits do not require the entire document set.

- GNU/Linux, Bash entry points, Python 3.11+ shared engine. Modules have no import-time operations.
- Keep per-tool wrappers thin. `lib/catalog.json` owns tools and generated documentation.
- Preserve filename bytes through argument arrays. Never use shell evaluation or follow input symlinks.
- Source files are retained. Writes require `--apply`. Publish verified outputs without overwriting existing paths.
- Test only disposable fixtures with isolated HOME/XDG paths. Network access is not a media feature.
- Preserve exit codes 0 success, 1 operation failure, 2 usage/dependency failure.
- Run `make check test-all` before publication. Report dependency skips honestly.
- Update generated tools, docs, and site with `make generate`, then run `make check`.

## Planning and evidence

Use the [project guide](.specify/memory/project-guide.md) and
[constitution](.specify/memory/constitution.md) for substantial changes. The guide
owns Spec Kit scope, retained history, retrospective requirements, and acceptance
evidence. Prose maintenance uses the normal repository workflow.

## Context and handoffs

- Search before reading. Use bounded source excerpts for exploratory reads over
  350 lines, and inspect required guidance and actual source before editing.
- When delegation is permitted, assign a bounded question or output, paths, and
  check. Return source locations, changes, and verification gaps for final review.
- Keep durable corrections in the [project guide](.specify/memory/project-guide.md)
  or owning contract. Replace superseded advice and read it before reuse.
  Temporary progress belongs in task notes. Preserve existing authority rules.
