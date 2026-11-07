#!/usr/bin/env bash
# Run the same pinned correctness and workflow policy as the retained hosted gates.
set -euo pipefail
root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)
git_local_environment=$(git rev-parse --local-env-vars)
while IFS= read -r git_variable; do unset "$git_variable"; done <<<"$git_local_environment"
export GIT_CONFIG_NOSYSTEM=1 GIT_CONFIG_GLOBAL=/dev/null
cd -- "$root"
test "$(git rev-parse --show-toplevel)" = "$root"
scratch=$(mktemp -d "${TMPDIR:-/tmp}/utility-ci-policy.XXXXXX")
trap 'rm -rf -- "$scratch"' EXIT
export PIP_NO_CACHE_DIR=1 npm_config_cache="$scratch/npm-cache"
python3 -m venv "$scratch/venv"
"$scratch/venv/bin/pip" install --disable-pip-version-check ruff==0.15.20 zizmor==1.29.0
export PATH="$scratch/venv/bin:$scratch:$PATH"
tooling=7603518f305fb76f7bb1b9979f2692521f633b82
git init --quiet "$scratch/tooling"
git -C "$scratch/tooling" fetch --quiet --depth=1 https://github.com/bolens/.github.git "$tooling"
git -C "$scratch/tooling" checkout --quiet --detach FETCH_HEAD
test "$(git -C "$scratch/tooling" rev-parse HEAD)" = "$tooling"
npm ci --ignore-scripts --no-audit --no-fund --prefix "$scratch/tooling/tools/source-lint"
python3 "$scratch/tooling/scripts/lint-source.py" "$root"
curl --fail --silent --show-error --location --retry 3 \
  --output "$scratch/actionlint.tar.gz" \
  https://github.com/rhysd/actionlint/releases/download/v1.7.12/actionlint_1.7.12_linux_amd64.tar.gz
printf '%s  %s\n' 8aca8db96f1b94770f1b0d72b6dddcb1ebb8123cb3712530b08cc387b349a3d8 "$scratch/actionlint.tar.gz" | sha256sum --check --strict
tar -xzf "$scratch/actionlint.tar.gz" -C "$scratch" actionlint
actionlint
zizmor --offline --min-severity medium --min-confidence medium .github
