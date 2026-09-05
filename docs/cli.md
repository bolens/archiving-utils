# CLI contract

```bash
bin/archiving-utils list
bin/archiving-utils TOOL --help
bin/archiving-utils library-inventory -- ./library
bin/archiving-utils hash-manifest -- ./library > manifest-response.json
```

Positional paths override configured roots. File inputs are explicit. Directory inputs recurse in deterministic order and skip symlinks. Each operation filters its supported extensions. Library tools include all regular files. No matches is a failure, not an empty success.

Writes require `--apply` plus `--output PATH` for a single input or `--output-dir DIR` for a batch. Without `--apply`, a write operation prints planned destinations. `--dry-run` takes precedence over `--apply` and suppresses report-file creation. Plans validate paths and collisions but do not run codecs or fully validate media.

Batch output names preserve relative paths and append the new suffix to the full filename. `album/photo.jpg` becomes `album/photo.jpg.png`. This avoids collisions between stems of different formats. Duplicate destinations across input roots fail before processing. Explicit output names need not match the encoded format. The catalog selects the actual encoder.

Outputs never replace existing files or directories. File outputs use same-filesystem temporary storage, verification, and atomic no-clobber publication. Archive extraction stages the entire tree and uses Linux `renameat2(RENAME_NOREPLACE)`. Parent directories may remain after a failed write. The operation does not promise crash-durable directory metadata or transactions spanning a whole batch. Successful outputs remain if another item fails.

Input trees and output parent directories must be under your control while a job runs. Concurrent edits to input files and hostile directory replacement are outside the supported contract. Sources are never deleted. A failed or interrupted process can leave temporary storage after an uncatchable kill, but incomplete files are not published under requested output names.

`-j N` runs 1 to 32 workers. Results retain discovery order. Progress is plain, complete lines on stderr. `-q` hides progress. JSON on stdout escapes control characters in filenames. `-S PATH` and `-L PATH` write new JSON reports and refuse existing paths. Reports are explicit writes even for inspection tools. A report publication failure makes the command fail.

Exit codes: **0** success, **1** operation or verification failure, **2** usage or missing dependency. Optional codec/delegate failures return 1 with encoder diagnostics. No ANSI output or spinners are used.

## Configuration

Optional JSON config: `$XDG_CONFIG_HOME/archiving-utils/config.json`, falling back to `$HOME/.config/archiving-utils/config.json`. `--config PATH` selects another file. It contains only `roots` as an array of path strings and `jobs` as an integer. Paths containing spaces need no special delimiter.

```json
{"roots": ["/path/to/library"], "jobs": 2}
```

Config is data and never executed as shell code. Reports are explicitly located by flags. There are no automatic persistent logs. Temporary files use the output filesystem for publication and `$TMPDIR` for domain staging.

## Hash manifests

`hash-manifest` emits the standard response envelope. Save its `results` array as the manifest accepted by `hash-verify`:

```bash
bin/archiving-utils hash-manifest ./library | python3 -c 'import json,sys; print(json.dumps(json.load(sys.stdin)["results"]))' > manifest.json
bin/archiving-utils hash-verify --manifest manifest.json ./library
```

Keep the manifest outside the scanned tree. Verification checks the full path set and every SHA-256 hash. Use one root with unique relative paths. `tree-diff` reports differences as data and returns success when the comparison itself completed.
