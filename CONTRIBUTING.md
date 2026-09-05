# Contributing

Keep commands focused and tool directories thin. Add catalog entries in `lib/catalog.json` and domain behavior in `lib/domain.py`. Shared CLI and file handling live in `lib/core.py`. Run `make generate` after catalog or help changes.

Add fixture-based coverage for observable behavior and failure cases. Run `make check test-all` before opening a pull request. Report optional dependency skips. Never use a personal library as test data.

Explain what changed, why, and which tests ran in pull requests. Keep output verification, source retention, offline defaults, and filename handling intact.
