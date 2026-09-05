# Changelog

## Unreleased

- Add `library-summary` to the CLI and read-only MCP server for file counts, total bytes, empty files, size ranges, and extension totals without reading media contents.

- Verify saved `hash-manifest` responses directly, while retaining support for bare entry arrays. Reject malformed manifests and ambiguous relative paths.
- Skip hashing files with unique byte sizes during duplicate detection.
- Bound queued batch operations to twice the worker count while preserving report order.

## 0.1.0

Initial command suites with source retention, verified output publication, batch processing, JSON reports, read-only MCP, fixture tests, and a searchable GitHub Pages command index with an Archify architecture diagram.
