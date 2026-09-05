# archiving-utils delivery playbook

This repository delivers reviewed source and its generated site from `main`.
`VERSION` is the CLI version authority. There is no versioned artifact release
workflow. Do not invent release tags or package publication for documentation or CI maintenance.

## Prepare and validate

Branch from current `origin/main` in a clean worktree. Preserve unrelated work.
Run `make check test-all` using disposable fixtures; report dependency skips.
For catalog/help changes run `make generate` and verify the generated output.
Workflow changes also require `actionlint` and
`zizmor --offline --min-severity medium --min-confidence medium .github`.
Review the full diff and new history for secrets and personal paths.

## Push, merge, and verify

Create a focused Conventional Commit, then run
`git push --set-upstream origin HEAD` and open a PR against `main`.
Require both Python test jobs and every applicable current-head check, review
the complete diff, resolve conversations, and squash-merge. Administrators
follow the same protections. Zero approving reviews support solo maintenance;
force pushes and default-branch deletion are disabled.

Verify CI on the merged SHA and the existing Pages deployment when applicable.
Delete only the verified merged feature branch. Never bypass protection or
use a personal media library as a publication smoke test.

## Recover and future releases

Repair or revert through a new reviewed PR. Preserve source media and existing
outputs during recovery. Before the first versioned release, define the artifact contract, verification,
and rollback procedure, and tie `VERSION` and the tag to an immutable source SHA.

Fleet policy: <https://github.com/bolens/.github/blob/main/RELEASING.md>.

## Source lint

The Source lint workflow checks maintained python, javascript, css files selected by
[`.github/source-lint.json`](.github/source-lint.json) on every pull request
and push to `main`. Existing native checks remain part of the merge gate.
Use the [shared local reproduction instructions](https://github.com/bolens/.github/blob/7603518f305fb76f7bb1b9979f2692521f633b82/docs/source-lint.md)
with the same tooling revision pinned in
[the workflow](.github/workflows/source-lint.yml). Review exclusions when adding
source files; generated and imported files retain their native validation.
Require the new check to pass on the current PR head before merging.
