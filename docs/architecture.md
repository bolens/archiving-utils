# Architecture

[Interactive Archify diagram](https://bolens.github.io/archiving-utils/diagrams/architecture.html) · [Diagram source](diagrams/architecture.json)

`bin/archiving-utils` dispatches to `lib/core.py`. Per-tool Bash scripts and Makefiles are generated from `lib/catalog.json`. The catalog owns names, descriptions, extensions, output formats, and operation types.

The shared core parses flags and JSON config, discovers regular files, plans destinations, rejects collisions, and submits work to a bounded thread pool with at most two outstanding operations per worker. File discovery and result collection still use memory proportional to the input count. Domain operations live in `lib/domain.py`. A writer creates temporary output, validates it, and calls no-clobber publication. Read-only operations return structured records. Library operations such as hashing and tree comparison run in the shared core.

`mcp/server.py` shares that engine but exposes a smaller read-only catalog. It requires allowed roots at startup and never accepts arbitrary CLI arguments. The MCP server is local stdio only.

`make generate` builds command wrappers, CLI reference pages, the catalog, and `site/index.html`. Site search and theme controls run locally in the browser. The website never accesses media files. GitHub Pages deploys the checked `site/` directory after CI succeeds on main.

The Archify specification is maintained separately from the website generator. `deliver` receipts and browser checks are stored in the documentation evidence directory. Generated HTML stays unchanged after delivery.

Comic commands use the same catalog and domain pipeline. `lib/comics.py` classifies
page extensions and natural filename order without decoding media or parsing
sidecars. `lib/archive_backend.py` lazily loads libarchive for RAR/7z/Zstandard and
streams each entry through the shared member validator. It never calls native
extract-to-disk functions. Each operation owns its native handle. bsdtar only
writes validated source trees for CB7/Zstandard; outputs are scanned and compared
with source file hashes and directory names before no-clobber publication.

`lib/rar5_checksums.py` independently validates bounded RAR5 headers and exposes
per-member CRC32 values. The streaming reader compares these against decoded
bytes before any staged output is published. This avoids relying on the native
stored-RAR5 checksum path. CRC-less RAR5 files are refused explicitly.
