# Woodpecker compatibility checks

[Documentation](README.md)

The existing Woodpecker workflow retains its locked Linux `devenv test` and adds
explicit Python 3.11 and 3.14 compatibility steps. Each pinned Debian Trixie image
asserts its interpreter version before running `make PYTHON=python3 check test-all`.
Test subprocesses resolve the same image interpreter. Fixtures receive private
HOME/XDG/TMPDIR paths; no host library or Docker socket is mounted.

`bash scripts/ci/check-python.sh 3.11` (or `3.14`) is the lane entrypoint. It
requires the real domain backend before invoking tests, so a missing core tool
cannot silently turn the functional suite into a skip. Existing optional format
or codec skips remain visible in unittest output. Native job logs retain the
combined check/test output and the producer exit code; the helper removes its
private temporary report and environment on success or failure.

Both compatibility lanes install `libarchive-tools`, run `bsdtar --version` and require the actual libarchive shared library before the full comic/archive tests.

`bash scripts/ci/check-policy.sh` runs the same pinned shared maintained-source
policy as the hosted Source lint workflow, followed by actionlint 1.7.12 and
zizmor 1.29.0 with offline medium-severity/medium-confidence thresholds. It
fetches immutable tooling revision `7603518f305fb76f7bb1b9979f2692521f633b82`, uses
Ruff 0.15.20 and its locked Node dependencies, and removes invocation-owned
tooling, caches and the Python environment. Checks are credential-free.

## Repository CI groups

The current workflow identity remains `woodpecker`; required statuses keep that
identity until a separately reviewed migration. Use these canonical entrypoints
for local reproduction and Woodpecker execution:

| Group | Woodpecker step | Local entrypoint |
| --- | --- | --- |
| validate | `development-environment` | `devenv test` |
| validate | `source-and-workflow-policy` | `bash scripts/ci/check-policy.sh` |
| test | `test-python-3-11` | `bash scripts/ci/check-python.sh 3.11` |
| test | `test-python-3-14` | `bash scripts/ci/check-python.sh 3.14` |
| site | retained hosted CI/Pages chain | existing checked site and Pages contract |
| publish | retained hosted Docker/GHCR | `make test-docker`; publication stays on trusted main |

The Python helper delegates to the existing `make check test-all` command rather
than copying tests. Local compatibility reproduction requires the selected
interpreter first on PATH and the same real backend packages as the lane image.
The policy helper uses public downloads into a private temporary directory; it
does not install tools into the developer's environment.

## Delivery boundary

Require actual native PR and genuine-main success for all four steps, plus every
applicable retained hosted check. These additions do not disable or replace
protected GitHub check names. The hosted CI workflow remains the Pages
`workflow_run` prerequisite and retains its weekly schedule and downloadable test
evidence. A future exact-source handoff or protected-check migration needs its
own accepted source, settings and event proof; an old green status on an unchanged
commit does not establish a fresh weekly run.

GitHub retains Python compatibility during this transition, macOS and actual
Docker/editor development validation, Docker runtime/GHCR publication, Pages/OIDC
and forge-only update automation. This change creates no release tag or product
version. Recover through a corrective or revert PR without changing media.
