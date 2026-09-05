# Relationship to audio-utils

These repositories adopt audio-utils' purpose and layout: small Linux commands for library conversion, inspection, and maintenance, backed by shared logic and a test harness.

| Convention | Sibling implementation |
|---|---|
| Thin per-tool directories | Generated Bash wrappers and Makefiles under conversion/ and util/category/ |
| Shared processing | Python core and domain modules, with no import-time processing |
| Preservation | Sources retained, verified temporary outputs, no-clobber publication |
| Batch work | Recursive discovery, deterministic reports, 1 to 32 workers |
| Filenames | Argument arrays, escaped JSON, no source symlink traversal |
| Read-only utilities | Inventory, exact duplicates, checksums, comparisons, domain reports |
| CLI contract | Plain stderr progress, JSON stdout, 0/1/2 exit codes |
| Configuration | XDG JSON roots and jobs, no shell evaluation |
| MCP | Local stdio, read-only tools, explicit allowed roots |
| Development | Make checks, fixture tests, generated-doc checks, optional pre-commit hook |
| Documentation | Indexed commands, limitations, contribution and release notes |
| Publishing | Public GitHub repository, CI, distinct Pages site, Archify diagram |

Differences are intentional: Python 3.11+ is required, write operations require `--apply`, no deletion flags exist, logs are explicit paths, and the MCP server has no write mode or npm gateway. The sibling suites do not claim the years of codec and domain edge-case coverage represented by audio-utils. Format-specific omissions are listed in `formats.md`.
