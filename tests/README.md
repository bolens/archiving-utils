# Tests

`make test` runs shared CLI, publication, filename, configuration, and MCP tests.
`make test-functional` runs real domain operations on generated fixtures.
`make test-all` runs both tiers and repository-validation tests. Tests use disposable fixtures. CLI subprocesses receive isolated HOME, XDG config/state/cache/data/runtime paths, and TMPDIR values.

Archive tests exercise compression and packaging formats, malicious member paths, links, duplicates, limits, corruption, extraction, and batch collisions.

Archive functional tests use Python standard-library modules and have no optional codec skip tier. The unittest report names every skip. CI installs the core dependencies and retains the report as an artifact. Tests require no personal media and perform no network enrichment.

Shared regression tests also cover direct manifest-response round trips, malformed and ambiguous manifests, size-filtered duplicate hashing, and bounded batch submission with stable result ordering.

Summary tests cover extension grouping, zero-byte files, overlapping roots, symlink exclusion, write refusal, MCP access, and operation without reading contents or invoking codecs.

Exclusion tests cover repeated and case-sensitive patterns, relative paths, multiline names, both comparison roots, full manifest filtering, write plans, and folder-packing refusal.
