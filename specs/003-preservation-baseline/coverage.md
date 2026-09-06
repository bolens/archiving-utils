# Requirement coverage

| Requirement | Source and acceptance evidence |
| --- | --- |
| FR-001 | `lib/catalog.json`, `scripts/generate.py`, and `scripts/check.py` generated-drift checks. |
| FR-002 | `lib/core.py:execute` and `publish`; `tests/test_common.py` covers failed writers/verifiers, publication races, cleanup, and preserved existing files. |
| FR-003 | `lib/core.py:discover` and `execute`; common filename, exclusion, collision, and mixed-batch tests. |
| FR-004 | `lib/domain.py`, `lib/archive_backend.py`, and archive functional tests cover all standard pack/repack formats, byte/name round trips, malicious members, and corruption. Existing comic tests cover native formats. |
| FR-005 | `lib/core.py:common`, catalog read operations, manifest-response round trips, no-content-read summary tests, and comparison tests. |
| FR-006 | `mcp/server.py`, allowed-root/initialize/request validation tests in `tests/test_common.py`. |
| FR-007 | `lib/core.py:ordered_work` and `execute`; common scheduling tests and mixed valid/corrupt functional batches with one and two workers. |

## Verification receipt

On 2026-09-05, `make check test-all` passed 89 tests with no failures or skips against the inspected base. `make check` also passed after adding this baseline. A separate self-review traced catalog generation, dry-run authority, discovery, staged verification and publication, batch failures, and MCP restrictions through the named source and test assertions. No unresolved requirement gap was found within this baseline. This proves the named fixture contracts, not every possible media file or external parser implementation. Hosted checks and delivery are recorded in the PR.
