# archiving-utils delivery playbook

This repository delivers reviewed source and its generated site from `main`.
There is no versioned artifact release workflow. Do not invent release tags or
package publication for documentation or CI maintenance.

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
outputs during recovery. A future versioned release needs an explicit version
authority, artifact contract, immutable source SHA, verification, and rollback
procedure before its first tag. No product release is needed for this setup.

Fleet policy: <https://github.com/bolens/.github/blob/main/RELEASING.md>.
