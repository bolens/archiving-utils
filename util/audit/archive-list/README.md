# archive-list

List members with sizes and SHA-256 hashes.

Mode: **read**. Operation: `list`.

Source extensions: `.zip`, `.tar`, `.tar.gz`, `.tgz`, `.tar.bz2`, `.tbz2`, `.tar.xz`, `.txz`, `.cbz`, `.cbr`, `.cb7`, `.cbt`, `.cbt.gz`, `.cbt.bz2`, `.cbt.xz`, `.cbt.zst`, `.cba`, `.rar`, `.7z`, `.tar.zst`, `.tzst`.

Run from the repository root:

```bash
bin/archiving-utils archive-list --help
```

Prints JSON to stdout. Does not modify inputs.

[CLI contract](../../../docs/cli.md) · [Formats and limits](../../../docs/formats.md)

## Options

| Argument | Purpose |
|---|---|
| `-h / --help` | show this help message and exit |
| `paths` | files or recursively scanned directories; use -- before leading dashes |
| `--exclude EXCLUDE` | exclude relative file paths matching a case-sensitive glob; repeatable |
| `--config CONFIG` | JSON config, defaults to XDG_CONFIG_HOME/archiving-utils/config.json |
| `--apply` | execute output-producing operations |
| `-n / --dry-run` | plan without writes |
| `-j / --jobs JOBS` | parallel workers, 1 to 32 |
| `-q / --quiet` | suppress progress on stderr |
| `-o / --output OUTPUT` | explicit output for one input |
| `--output-dir OUTPUT_DIR` | batch output tree preserving relative paths |
| `--against AGAINST` | comparison tree or reference image |
| `--manifest MANIFEST` | JSON SHA-256 manifest for hash-verify |
| `-S / --success-log SUCCESS_LOG` | new JSON success report |
| `-L / --failure-log FAILURE_LOG` | new JSON failure report |
| `--size SIZE` | image bounding box WIDTHxHEIGHT |
| `--quality QUALITY` | image quality 1 to 100 |
| `--start START` | video start time in seconds |
| `--duration DURATION` | video clip duration in seconds |
| `--max-bytes MAX_BYTES` | archive uncompressed-byte limit |
| `--max-members MAX_MEMBERS` | archive member-count limit |
