# Tests

`make test` runs shared CLI, publication, filename, configuration, and MCP tests.
`make test-functional` runs real domain operations on generated fixtures.
`make test-all` runs both tiers. All tests use disposable directories and isolated HOME/XDG/TMPDIR values.

Archive tests exercise every compression and packaging format, malicious member paths, links, duplicates, limits, corruption, extraction, and batch collisions. Image tests exercise conversion delegates, transforms, metadata, animation refusal, and thumbnail bounds. Video tests exercise container remuxing, encoders, transforms, stream reports, corruption, and parallel poster generation.

Optional ImageMagick delegates may skip a format subtest. The unittest report names every skip. CI installs the core dependencies and retains the report as an artifact. Tests require no personal media and perform no network enrichment.

Shared regression tests also cover direct manifest-response round trips, malformed and ambiguous manifests, size-filtered duplicate hashing, and bounded batch submission with stable result ordering.
