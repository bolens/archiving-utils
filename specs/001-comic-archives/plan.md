# Implementation plan

See [specification](spec.md). Base: 04eb30bf529fa0bcd8229c6621f51de067bc66c7.

Primary agent owns this isolated worktree and all feature changes. Other fleet lint worktrees are excluded.

## Architecture

- lib/domain.py remains the archive contract owner. One member consumer validates names/types/limits and hashes streamed bytes for every backend.
- lib/archive_backend.py lazily binds the libarchive C reader API through ctypes. Register only needed formats and native filters. Never use a native extract-to-disk API or parse human-readable listings. Each operation owns its handle and frees it on every exit.
- bsdtar only packages already validated source trees for 7z/Zstandard output. Verify outputs through the same bounded scanner before publication. Existing ZIP/TAR operations retain their standard-library implementation.
- lib/comics.py owns extension-based page classification and deterministic natural ordering. Catalog owns commands and generated wrappers/docs/site.
- tests/test_comics.py owns comic and native-backend coverage. Existing common and archive tests protect prior behavior. Make functional tier includes the new file. CI adds only backend packages to the existing test jobs.

## Constitution check

No safety reduction, source deletion, overwrite, network media operation or new MCP authority. Existing standard-library codecs remain. The optional bounded native backend is an additive format capability. Formats and dependency documentation must describe the decoder limits and RAR read-only boundary.

## Evidence and delivery

Run focused tests, make generate, make check test-all, actionlint and offline zizmor. Use separate behavior/security and tests/delivery reviews. Commit specification, implementation/tests, and generated documentation in focused groups. Scan new history, create PR, require all checks, squash merge, verify main CI/Pages and synchronize the original clean main checkout.
