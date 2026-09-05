# Tests

`make test` runs shared CLI, publication, filename, configuration, and MCP tests.
`make test-functional` runs real domain operations on generated fixtures.
`make test-all` runs both tiers and repository-validation tests. Tests use disposable fixtures. CLI subprocesses receive isolated HOME, XDG config/state/cache/data/runtime paths, and TMPDIR values.

Archive tests exercise compression and packaging formats, malicious member paths, links, duplicates, limits, corruption, extraction, and batch collisions.

Original archive functional tests use Python standard-library modules. Comic native-format tests require libarchive and bsdtar and report an explicit skip when unavailable. CI requires those backends. The unittest report names every skip. CI installs the core dependencies and retains the report as an artifact. Tests require no personal media and perform no network enrichment.

Shared regression tests also cover direct manifest-response round trips, malformed and ambiguous manifests, size-filtered duplicate hashing, and bounded batch submission with stable result ordering.

Summary tests cover extension grouping, zero-byte files, overlapping roots, symlink exclusion, write refusal, MCP access, and operation without reading contents or invoking codecs.

Exclusion tests cover repeated and case-sensitive patterns, relative paths, multiline names, both comparison roots, full manifest filtering, write plans, and folder-packing refusal.

Publication checks cover writer failure, missing output, rejected verification, sync/link failures, existing destinations, and two concurrent publishers. They assert that failed outputs stay unpublished and staging files are removed.

Mixed valid/corrupt batches run with one and two workers. Functional checks verify successful output, source retention, absent failed output, nonzero exit status, and matching success/failure reports. These cases run in the existing `make test` and `make test-functional` tiers, and together in `make test-all`.

Archive round-trip checks compare every relative name, file byte, and directory after packing and repacking each ZIP/TAR variant. Fixtures include nested empty directories and Unicode, glob, and newline names.

Comic tests run in `make test-functional` and `make test-all`. They exercise all
seven creation formats, all 49 conversion pairs, full extraction comparisons,
RAR4 and stored/compressed RAR5 conversion, extension-based page inventories,
sidecar retention, source retention, dry runs, collisions, partial batches,
unsafe paths, native links, encryption, missing volumes, checksum corruption,
limits and unavailable dependencies. Pinned upstream RAR fixtures and license
notices live in `tests/fixtures/libarchive`. Test page payloads are opaque synthetic
bytes because this feature verifies containers, not image decoding.
