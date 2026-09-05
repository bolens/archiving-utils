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

`-j N` runs 1 to 32 workers, with at most twice that many operations submitted at once. Results retain discovery order. Discovery and JSON reports still retain the full file list in memory. Progress is plain, complete lines on stderr. `-q` hides progress. JSON on stdout escapes control characters in filenames. `-S PATH` and `-L PATH` write new JSON reports and refuse existing paths. Reports are explicit writes even for inspection tools. A report publication failure makes the command fail.

Exit codes: **0** success, **1** operation or verification failure, **2** usage or missing dependency. Optional codec/delegate failures return 1 with encoder diagnostics. No ANSI output or spinners are used.

## Configuration

Optional JSON config: `$XDG_CONFIG_HOME/archiving-utils/config.json`, falling back to `$HOME/.config/archiving-utils/config.json`. `--config PATH` selects another file. It contains only `roots` as an array of path strings and `jobs` as an integer. Paths containing spaces need no special delimiter. Configuration files and their parent paths must not be symlinks. A rejected configuration exits with code 2. A dangling default-config symlink is an error, while an absent default configuration remains optional.

```json
{"roots": ["/path/to/library"], "jobs": 2}
```

Config is data and never executed as shell code. Reports are explicitly located by flags. There are no automatic persistent logs. Temporary files use the output filesystem for publication and `$TMPDIR` for domain staging.

## Hash manifests

`hash-manifest` emits the standard response envelope, which `hash-verify` accepts directly:

```bash
bin/archiving-utils hash-manifest ./library > manifest.json
bin/archiving-utils hash-verify --manifest manifest.json ./library
```

Existing manifests containing only the `results` array remain supported. Verification rejects malformed entries, failed response envelopes, non-relative paths, duplicate paths, and invalid SHA-256 values. Hexadecimal checksums may use either case. Generation rejects duplicate relative paths across input roots before hashing.

Manifest files and their parent paths must not be symlinks. A rejected manifest exits with code 1. Keep the manifest outside the scanned tree. Verification checks the full path set and every SHA-256 hash. Use one root with unique relative paths. `tree-diff` reports differences as data and returns success when the comparison itself completed.

## Duplicate detection

`library-dupes` first groups files by byte size and hashes only files whose size occurs more than once. Same-size files still require matching full SHA-256 hashes. Results preserve discovery order and never delete or modify files.

## Collection summary

```bash
bin/archiving-utils library-summary ./library
```

The response contains one summary in `results`: `file_count`, `total_bytes`, `empty_files`, `min_bytes`, `max_bytes`, and an `extensions` array with counts and byte totals. Sizes are logical file bytes, not allocated disk space. No file contents are read and no codecs run. This command does not verify media integrity.

Extensions use the lowercase final suffix, so `.JPG` and `.jpg` share a group and `collection.tar.gz` is grouped under `.gz`. An empty extension represents names without a suffix, including `.hidden` and names ending in a dot. Extension groups sort by name. Overlapping input paths count each discovered path once. Distinct hard-link paths count separately. Symlinks are skipped during directory discovery. Empty input trees retain the usual no-matches failure.

`library-summary` is also available through the read-only MCP server, with the same allowed-root restrictions as inventory.

## Source exclusions

```bash
bin/archiving-utils library-summary --exclude 'previews/*' --exclude '*.tmp' ./library
```

Repeat `--exclude GLOB` to omit any matching file. Quote globs to prevent shell expansion. Matching is case-sensitive against each file's relative path using `/` separators. Explicit file inputs match their basename. `*` matches across separators, `?` matches one character, and bracket patterns match character sets. Hidden files follow the same rules. No shell evaluation occurs.

Exclusions filter discovered files before hashing, planning outputs, or invoking codecs. Discovery still traverses directories and reports traversal errors. Tree comparisons apply exclusions to both roots. Manifest verification validates the complete manifest schema, then excludes matching expected entries as well as actual files. If no input files remain, the normal no-matches failure applies. Exclusions do not modify sources.

Folder-packing commands reject exclusions rather than silently ignoring them. For archive conversion and extraction, exclusions select source archive files, not members inside an archive. MCP continues to accept only its existing allowed-root paths argument.
