# Agent guidance

Read `docs/architecture.md`, `docs/requirements.md`, and `tests/README.md`.

- GNU/Linux, Bash entry points, Python 3.11+ shared engine. Modules have no import-time operations.
- Keep per-tool wrappers thin. `lib/catalog.json` owns tools and generated documentation.
- Preserve filename bytes through argument arrays. Never use shell evaluation or follow input symlinks.
- Source files are retained. Writes require `--apply`. Publish verified outputs without overwriting existing paths.
- Test only disposable fixtures with isolated HOME/XDG paths. Network access is not a media feature.
- Preserve exit codes 0 success, 1 operation failure, 2 usage/dependency failure.
- Run `make check test-all` before publication. Report dependency skips honestly.
- Update generated tools, docs, and site with `make generate`, then run `make check`.

## Spec-driven changes

Read `.specify/memory/constitution.md` and `.specify/memory/project-guide.md`
before planning substantial changes. Use Spec Kit for new capabilities,
architecture, security-sensitive behavior, migrations, and coordinated changes.
Keep narrow fixes and prose maintenance in the normal PR workflow. Retain
completed feature history; do not backfill specifications for finished code.
Follow `RELEASING.md` for push, merge, delivery, and recovery.
