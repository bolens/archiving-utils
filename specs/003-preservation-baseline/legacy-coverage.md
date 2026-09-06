# Legacy coverage

Audit at `55213152571d6c23520d408ba81a4c49d15fd10f`, 2026-09-06.
All 48 catalog tools are assigned below. Shared LC-001–004 apply to every CLI
command; LC-013 applies only to the restricted read-only MCP selection. Detailed
behavior is in [legacy contracts](legacy-contracts.md), with per-command options
in the incorporated [CLI reference](../../docs/cli.md). Fixture links identify
acceptance owners; they do not claim a live library or external service was tested.

| Tool | Contract | Domain implementation | Acceptance fixtures |
| --- | --- | --- | --- |
| `library-inventory` | LC-009 | [lib/core.py](../../lib/core.py) | [tests/test_common.py](../../tests/test_common.py) |
| `library-summary` | LC-009 | [lib/core.py](../../lib/core.py) | [tests/test_common.py](../../tests/test_common.py) |
| `library-dupes` | LC-010 | [lib/core.py](../../lib/core.py) | [tests/test_common.py](../../tests/test_common.py) |
| `hash-manifest` | LC-011 | [lib/core.py](../../lib/core.py) | [tests/test_common.py](../../tests/test_common.py) |
| `hash-verify` | LC-011 | [lib/core.py](../../lib/core.py) | [tests/test_common.py](../../tests/test_common.py) |
| `tree-diff` | LC-012 | [lib/core.py](../../lib/core.py) | [tests/test_common.py](../../tests/test_common.py) |
| `path-audit` | LC-012 | [lib/core.py](../../lib/core.py) | [tests/test_common.py](../../tests/test_common.py) |
| `folder-to-zip` | LC-005 | [lib/domain.py](../../lib/domain.py) | [tests/test_functional.py](../../tests/test_functional.py) |
| `archive-to-zip` | LC-005 | [lib/domain.py](../../lib/domain.py) | [tests/test_functional.py](../../tests/test_functional.py) |
| `folder-to-tar` | LC-005 | [lib/domain.py](../../lib/domain.py) | [tests/test_functional.py](../../tests/test_functional.py) |
| `archive-to-tar` | LC-005 | [lib/domain.py](../../lib/domain.py) | [tests/test_functional.py](../../tests/test_functional.py) |
| `folder-to-tar-gz` | LC-005 | [lib/domain.py](../../lib/domain.py) | [tests/test_functional.py](../../tests/test_functional.py) |
| `archive-to-tar-gz` | LC-005 | [lib/domain.py](../../lib/domain.py) | [tests/test_functional.py](../../tests/test_functional.py) |
| `folder-to-tar-bz2` | LC-005 | [lib/domain.py](../../lib/domain.py) | [tests/test_functional.py](../../tests/test_functional.py) |
| `archive-to-tar-bz2` | LC-005 | [lib/domain.py](../../lib/domain.py) | [tests/test_functional.py](../../tests/test_functional.py) |
| `folder-to-tar-xz` | LC-005 | [lib/domain.py](../../lib/domain.py) | [tests/test_functional.py](../../tests/test_functional.py) |
| `archive-to-tar-xz` | LC-005 | [lib/domain.py](../../lib/domain.py) | [tests/test_functional.py](../../tests/test_functional.py) |
| `file-to-gz` | LC-006 | [lib/domain.py](../../lib/domain.py) | [tests/test_functional.py](../../tests/test_functional.py) |
| `gz-to-file` | LC-006 | [lib/domain.py](../../lib/domain.py) | [tests/test_functional.py](../../tests/test_functional.py) |
| `gz-verify` | LC-006 | [lib/domain.py](../../lib/domain.py) | [tests/test_functional.py](../../tests/test_functional.py) |
| `file-to-bz2` | LC-006 | [lib/domain.py](../../lib/domain.py) | [tests/test_functional.py](../../tests/test_functional.py) |
| `bz2-to-file` | LC-006 | [lib/domain.py](../../lib/domain.py) | [tests/test_functional.py](../../tests/test_functional.py) |
| `bz2-verify` | LC-006 | [lib/domain.py](../../lib/domain.py) | [tests/test_functional.py](../../tests/test_functional.py) |
| `file-to-xz` | LC-006 | [lib/domain.py](../../lib/domain.py) | [tests/test_functional.py](../../tests/test_functional.py) |
| `xz-to-file` | LC-006 | [lib/domain.py](../../lib/domain.py) | [tests/test_functional.py](../../tests/test_functional.py) |
| `xz-verify` | LC-006 | [lib/domain.py](../../lib/domain.py) | [tests/test_functional.py](../../tests/test_functional.py) |
| `archive-extract` | LC-008 | [lib/domain.py](../../lib/domain.py) | [tests/test_functional.py](../../tests/test_functional.py) |
| `archive-list` | LC-007 | [lib/domain.py](../../lib/domain.py) | [tests/test_functional.py](../../tests/test_functional.py) |
| `archive-verify` | LC-007 | [lib/domain.py](../../lib/domain.py) | [tests/test_functional.py](../../tests/test_functional.py) |
| `archive-stats` | LC-007 | [lib/domain.py](../../lib/domain.py) | [tests/test_functional.py](../../tests/test_functional.py) |
| `archive-manifest` | LC-007 | [lib/domain.py](../../lib/domain.py) | [tests/test_functional.py](../../tests/test_functional.py) |
| `comic-info` | [spec 001](../001-comic-archives/spec.md), spec 001 | [lib/domain.py](../../lib/domain.py) | [tests/test_comic_functional.py](../../tests/test_comic_functional.py) |
| `comic-verify` | [spec 001](../001-comic-archives/spec.md), spec 001 | [lib/domain.py](../../lib/domain.py) | [tests/test_comic_functional.py](../../tests/test_comic_functional.py) |
| `comic-extract` | [spec 001](../001-comic-archives/spec.md), LC-008 | [lib/domain.py](../../lib/domain.py) | [tests/test_comic_functional.py](../../tests/test_comic_functional.py) |
| `folder-to-cbz` | [spec 001](../001-comic-archives/spec.md), LC-005 | [lib/domain.py](../../lib/domain.py) | [tests/test_comic_functional.py](../../tests/test_comic_functional.py) |
| `comic-to-cbz` | [spec 001](../001-comic-archives/spec.md), LC-005 | [lib/domain.py](../../lib/domain.py) | [tests/test_comic_functional.py](../../tests/test_comic_functional.py) |
| `folder-to-cb7` | [spec 001](../001-comic-archives/spec.md), LC-005 | [lib/domain.py](../../lib/domain.py) | [tests/test_comic_functional.py](../../tests/test_comic_functional.py) |
| `comic-to-cb7` | [spec 001](../001-comic-archives/spec.md), LC-005 | [lib/domain.py](../../lib/domain.py) | [tests/test_comic_functional.py](../../tests/test_comic_functional.py) |
| `folder-to-cbt` | [spec 001](../001-comic-archives/spec.md), LC-005 | [lib/domain.py](../../lib/domain.py) | [tests/test_comic_functional.py](../../tests/test_comic_functional.py) |
| `comic-to-cbt` | [spec 001](../001-comic-archives/spec.md), LC-005 | [lib/domain.py](../../lib/domain.py) | [tests/test_comic_functional.py](../../tests/test_comic_functional.py) |
| `folder-to-cbt-gz` | [spec 001](../001-comic-archives/spec.md), LC-005 | [lib/domain.py](../../lib/domain.py) | [tests/test_comic_functional.py](../../tests/test_comic_functional.py) |
| `comic-to-cbt-gz` | [spec 001](../001-comic-archives/spec.md), LC-005 | [lib/domain.py](../../lib/domain.py) | [tests/test_comic_functional.py](../../tests/test_comic_functional.py) |
| `folder-to-cbt-bz2` | [spec 001](../001-comic-archives/spec.md), LC-005 | [lib/domain.py](../../lib/domain.py) | [tests/test_comic_functional.py](../../tests/test_comic_functional.py) |
| `comic-to-cbt-bz2` | [spec 001](../001-comic-archives/spec.md), LC-005 | [lib/domain.py](../../lib/domain.py) | [tests/test_comic_functional.py](../../tests/test_comic_functional.py) |
| `folder-to-cbt-xz` | [spec 001](../001-comic-archives/spec.md), LC-005 | [lib/domain.py](../../lib/domain.py) | [tests/test_comic_functional.py](../../tests/test_comic_functional.py) |
| `comic-to-cbt-xz` | [spec 001](../001-comic-archives/spec.md), LC-005 | [lib/domain.py](../../lib/domain.py) | [tests/test_comic_functional.py](../../tests/test_comic_functional.py) |
| `folder-to-cbt-zst` | [spec 001](../001-comic-archives/spec.md), LC-005 | [lib/domain.py](../../lib/domain.py) | [tests/test_comic_functional.py](../../tests/test_comic_functional.py) |
| `comic-to-cbt-zst` | [spec 001](../001-comic-archives/spec.md), LC-005 | [lib/domain.py](../../lib/domain.py) | [tests/test_comic_functional.py](../../tests/test_comic_functional.py) |

## Supporting surfaces

| Contract | Source owner | Acceptance owner and limits |
| --- | --- | --- |
| LC-001–004 | [CLI dispatcher](../../bin/archiving-utils), [shared core](../../lib/core.py), [catalog](../../lib/catalog.json), generated conversion/util wrappers and Makefiles | [Common tests](../../tests/test_common.py) cover help/wrappers, config, unusual names, exclusions, bounded workers, reports and publication races; [checkout tests](../../tests/test_checkout_portability.py) cover renamed/Unicode directories. |
| LC-005–008 / spec 001 | [Domain engine](../../lib/domain.py), [native backend](../../lib/archive_backend.py), [comic inventory](../../lib/comics.py), [RAR4 headers](../../lib/rar4_headers.py), [RAR5 checksums](../../lib/rar5_checksums.py) | [Functional tests](../../tests/test_functional.py), [comic matrix](../../tests/test_comic_functional.py), [header tests](../../tests/test_comic_headers.py). Optional native formats require their backend; pinned fixtures carry [license/provenance](../../tests/fixtures/libarchive/README.md). |
| LC-013 | [MCP server](../../mcp/server.py) | `test_mcp` / `test_mcp_bad_json` in [common tests](../../tests/test_common.py): root/input/write refusal, initialization and framing boundaries. |
| LC-014 | [Generator](../../scripts/generate.py), [checker](../../scripts/check.py), [shared Make rules](../../lib/tool.mk), [site](../../site/), [architecture source](../../docs/diagrams/architecture.json) | `make check` checks generated drift, source imports/syntax, local links and site contracts; [repository tests](../../tests/test_repository_checks.py) verify the checker. Browser evidence has its own [index](../../docs/evidence/README.md). |
| Existing spec 002 Docker | [Dockerfile](../../Dockerfile), [Docker acceptance](../../scripts/test-docker.py) | [Docker specification](../002-docker-runtime/spec.md); isolated runtime image tests and exact digest delivery gates, no live library. |
| Existing development specification | [Development launcher](../../scripts/development-container.py), devenv lock/config and [guide](../../docs/development-environments.md) | [Launcher tests](../../tests/test_development_container.py), [development tasks/receipts](../002-development-environments/tasks.md). |
| Delivery/governance | [Workflows](../../.github/workflows/), [hooks](../../.githooks/), [playbook](../../RELEASING.md), [Spec Kit memory/templates](../../.specify/) | Native and hosted validation, protected squash merge, main CI/Pages and GHCR digest verification where applicable. Spec Kit integration validation alone is not runtime proof. |

The original 31 archive/library commands now have explicit legacy contracts.
The 17 comic commands retain their existing detailed specification. New catalog
entries or materially changed behavior must update this mapping and acceptance
owners. Results/skips and delivery status belong in [coverage](coverage.md) and
the PR, not in claims inferred from an installed Spec Kit directory.
