# Tasks

- [x] Implement tailored tools, adapters, platform boundaries and documentation.
- [x] Pass full native Linux and actual Podman: 94 tests with no native backend skips.
- [x] Verify native Linux/macOS and Linux Docker checks on the recorded main revision.
- [x] Verify merged source delivery and the applicable main-revision workflows.

## Delivery verification — 2026-09-06

The [development workflow](https://github.com/bolens/archiving-utils/actions/runs/34034549192) passed on
`8723599b3c8de615fbd0b3ac53c9d702ae2f5280`. Both native platform jobs ran successfully;
the Linux job also executed and passed the Docker development-image check. All
applicable workflows observed for that main revision completed successfully.

Actual Apple container-engine execution remains unverified. Native macOS devenv
validation does not establish that engine's runtime behavior. Existing live-host
and optional dependency limits still apply. Checkout cleanup remains part of each
task's delivery procedure and is not inferred from CI success.
