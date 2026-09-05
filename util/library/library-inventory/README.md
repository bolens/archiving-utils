# library-inventory

List file sizes and relative paths.

Mode: **read**. Operation: `inventory`.

Run from the repository root:

```bash
bin/archiving-utils library-inventory --help
```

Prints JSON to stdout. Does not modify inputs.

[CLI contract](../../../docs/cli.md) · [Formats and limits](../../../docs/formats.md)

```text
usage: library-inventory [-h] [--config CONFIG] [--apply] [-n] [-j JOBS] [-q]
                         [-o OUTPUT] [--output-dir OUTPUT_DIR]
                         [--against AGAINST] [--manifest MANIFEST]
                         [-S SUCCESS_LOG] [-L FAILURE_LOG] [--size SIZE]
                         [--quality QUALITY] [--start START]
                         [--duration DURATION] [--max-bytes MAX_BYTES]
                         [--max-members MAX_MEMBERS]
                         [paths ...]

List file sizes and relative paths.

positional arguments:
  paths                 files or recursively scanned directories; use --
                        before leading dashes

options:
  -h, --help            show this help message and exit
  --config CONFIG       JSON config, defaults to XDG_CONFIG_HOME/archiving-
                        utils/config.json
  --apply               execute output-producing operations
  -n, --dry-run         plan without writes
  -j, --jobs JOBS       parallel workers, 1 to 32
  -q, --quiet           suppress progress on stderr
  -o, --output OUTPUT   explicit output for one input
  --output-dir OUTPUT_DIR
                        batch output tree preserving relative paths
  --against AGAINST     comparison tree or reference image
  --manifest MANIFEST   JSON SHA-256 manifest for hash-verify
  -S, --success-log SUCCESS_LOG
                        new JSON success report
  -L, --failure-log FAILURE_LOG
                        new JSON failure report
  --size SIZE           image bounding box WIDTHxHEIGHT
  --quality QUALITY     image quality 1 to 100
  --start START         video start time in seconds
  --duration DURATION   video clip duration in seconds
  --max-bytes MAX_BYTES
                        archive uncompressed-byte limit
  --max-members MAX_MEMBERS
                        archive member-count limit

Writes require --apply. Sources are retained. Existing outputs are never
overwritten. Exit: 0 success, 1 failure, 2 usage/dependency.
```
