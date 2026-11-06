# Portable Woodpecker validation

## Scope

Run the existing `archiving-utils` Linux development check on either `ci01` or `ci02`
at <https://woodpecker.bolens.dev>. This changes repository automation only.

## Acceptance

- Pull requests, main pushes, and manual validation run the locked `devenv test`.
- Disposable containers receive no host Docker socket, host Nix store, privileged
  mode, or publication secrets.
- A genuine current-head PR and merged-main pipeline must succeed before retiring
  the duplicate Linux native development check in GitHub Actions.
- Existing Python compatibility, macOS, Docker, and publishing checks retain their
  contracts until equivalent replacement evidence exists.
- No product version, source tag, or package release is created by this change.
