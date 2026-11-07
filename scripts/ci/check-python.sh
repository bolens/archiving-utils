#!/usr/bin/env bash
# Execute the supported Python compatibility lane on disposable local fixtures.
set -euo pipefail
if [[ $# != 1 || ! $1 =~ ^3\.(11|14)$ ]]; then
  printf 'usage: check-python.sh 3.11|3.14\n' >&2
  exit 2
fi
expected=$1
actual=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
if [[ $actual != "$expected" ]]; then
  printf 'Expected Python %s, found %s\n' "$expected" "$actual" >&2
  exit 2
fi
python3 --version
command -v bsdtar >/dev/null || { printf 'Required archive backend missing: bsdtar\n' >&2; exit 2; }
bsdtar --version
python3 -c 'import ctypes.util; assert ctypes.util.find_library("archive"), "Required libarchive shared library is missing"'
root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)
scratch=$(mktemp -d "${TMPDIR:-/tmp}/utility-python-ci.XXXXXX")
trap 'rm -rf -- "$scratch"' EXIT
mkdir -p "$scratch"/{home,config,cache,state,data,runtime,tmp}
cd -- "$root"
# The lane image puts the selected interpreter first for Make and test children.
# pipefail preserves the producer failure while retaining the native job log.
env HOME="$scratch/home" XDG_CONFIG_HOME="$scratch/config" XDG_CACHE_HOME="$scratch/cache" \
  XDG_STATE_HOME="$scratch/state" XDG_DATA_HOME="$scratch/data" XDG_RUNTIME_DIR="$scratch/runtime" \
  TMPDIR="$scratch/tmp" PYTHONDONTWRITEBYTECODE=1 \
  make PYTHON=python3 check test-all 2>&1 | tee "$scratch/test-results-python-$expected.txt"
