# Implementation plan

See [specification](spec.md). Base: 04eb30bf529fa0bcd8229c6621f51de067bc66c7.

Primary agent owns this isolated worktree and all feature changes. Other fleet lint worktrees are excluded.

## Architecture

- lib/domain.py remains the archive contract owner. One member consumer validates names/types/limits and hashes streamed bytes for every backend.
- lib/archive_backend.py lazily binds the libarchive C reader API through ctypes. Register only needed formats and native filters. Never use a native extract-to-disk API or parse human-readable listings. Each operation owns its handle and frees it on every exit.
- bsdtar only packages already validated source trees for 7z/Zstandard output. Verify outputs through the same bounded scanner before publication. Existing ZIP/TAR operations retain their standard-library implementation.
- lib/comics.py owns extension-based page classification and deterministic natural ordering. Catalog owns commands and generated wrappers/docs/site.
- tests/test_comic_functional.py owns comic and native-backend coverage. Existing common and archive tests protect prior behavior. Make functional tier includes the new file. CI adds only backend packages to the existing test jobs.

## Constitution check

No safety reduction, source deletion, overwrite, network media operation or new MCP authority. Existing standard-library codecs remain. The optional bounded native backend is an additive format capability. Formats and dependency documentation must describe the decoder limits and RAR read-only boundary.

## Evidence and delivery

Run focused tests, make generate, make check test-all, actionlint and offline zizmor. Use separate behavior/security and tests/delivery reviews. Commit specification, implementation/tests, and generated documentation in focused groups. Scan new history, create PR, require all checks, squash merge, verify main CI/Pages and synchronize the original clean main checkout.

## Investigation receipt

A stored RAR5 payload mutation was accepted by bsdtar/libarchive 3.8.9 but rejected
by unrar 7.23. Source inspection of libarchive's stored data/finalization paths
confirmed the independent-check need. Add bounded RAR5 header CRC validation and
per-file CRC32 comparison in rar5_checksums.py. Refuse CRC-less RAR5 entries rather
than claim their payload integrity. The same fixture now fails before extraction
publication. No extra RAR executable is required at runtime.
