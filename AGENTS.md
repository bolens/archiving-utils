# Agent guidance

Use `docs/architecture.md` for shared-engine or catalog changes,
`docs/requirements.md` for runtime or codec requirements, and `tests/README.md`
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

## Spec-driven changes

Read `.specify/memory/constitution.md` and `.specify/memory/project-guide.md`
before planning substantial changes. Use Spec Kit for new capabilities,
architecture, security-sensitive behavior, migrations, and coordinated changes.
Keep narrow fixes and prose maintenance in the normal PR workflow. Retain
completed feature history. Backfill finished work only when explicitly requested. Label those
specifications as retrospective baselines, record the inspected revision, and map
requirements to source and acceptance evidence. Separate observed behavior from
corrective requirements. Never imply the specification preceded its code or mark
unverified checks complete.
Follow `RELEASING.md` for push, merge, delivery, and recovery.

## Context and handoffs

- Locate source with targeted searches before reading. For exploratory reads of
  files over 350 lines, select relevant ranges. Read required guidance and actual
  source before edits or correctness claims; summaries do not replace them.
- When delegation is permitted, give each worker one question or concrete output,
  allowed paths, and a check. Return findings with source locations, changed paths,
  and verification gaps. Keep final review with the coordinating agent.
- Record durable user corrections in the [project guide](.specify/memory/project-guide.md)
  or owning contract with scope, reason, and evidence. Replace superseded advice;
  read relevant corrections before reusing assumptions. Keep temporary progress
  in task notes and preserve existing authority rules.
