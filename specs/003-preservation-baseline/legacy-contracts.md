# Legacy capability contracts

Retrospective audit at `55213152571d6c23520d408ba81a4c49d15fd10f`, 2026-09-06.
This extends [spec.md](spec.md) with the original archive/library command contracts.
[Legacy coverage](legacy-coverage.md) assigns every one of the 48 catalog tools
and the supporting entry points to its requirements and native fixtures.

## Authority and feature boundaries

The [CLI reference](../../docs/cli.md), [catalog](../../docs/catalog.md),
[formats and limits](../../docs/formats.md), [requirements](../../docs/requirements.md),
and [MCP guide](../../docs/mcp.md) are normative parts of this specification.
Generated command options remain owned by `lib/catalog.json` and the shared
parser. The 17 comic commands and their native readers/writers retain the more
specific [comic specification](../001-comic-archives/spec.md). Existing
[Docker](../002-docker-runtime/spec.md) and
[development environment](../002-development-environments/spec.md) specifications
remain authoritative for their respective delivery surfaces.

## Shared execution

- **LC-001, CLI/configuration:** Dispatcher help/list, version, generated command
  wrappers and Make aliases MUST retain the same catalog identities. JSON config
  accepts only `roots` and `jobs`; explicit paths/jobs take precedence. Config and
  path components must not be symlinks. Jobs are integers from 1 to 32, default 1.
  Unknown options/tools and invalid configuration return 2. No input matches
  return failure, including an empty tree. Archive byte/member limits must be
  positive. Inherited `--size`, `--quality`, `--start`, and `--duration` flags
  retain parser validation but do not transform archive contents.
- **LC-002, discovery/exclusions:** Regular-file discovery MUST recurse without
  following symlinks, deduplicate overlapping absolute paths, preserve filename
  bytes through argument arrays, and return stable bytewise path order. Extension
  matching is case-insensitive. Repeated exclusions match case-sensitive relative
  path globs, including newline names; empty patterns are invalid. Exclusions
  filter both tree-comparison sides and full expected/actual manifest sets.
  Folder packing rejects exclusions rather than silently creating an incomplete
  preservation package.
- **LC-003, write planning/publication:** Every writer MUST require an explicit
  output or output directory. Explicit output requires exactly one source;
  output-directory mode appends the catalog suffix to the relative source name.
  Reject duplicate target mappings, existing destinations, source replacements,
  and outputs nested in a packed source. Default execution plans writes;
  `--dry-run` overrides `--apply` and suppresses success/failure report writes.
  Applied writes verify private staging before no-clobber publication, retain
  sources, and remove failed staging. Concurrent publishers must have at most
  one winner. Directory extraction uses no-replace publication too.
- **LC-004, batches/results:** Bounded worker submission MUST retain at most
  twice the worker count outstanding jobs, preserve result order, and retain
  successful outputs when another source fails. JSON stdout separates results
  and failures; progress belongs on stderr unless quiet. Dependency failures
  return 2, other operation failures 1, successful execution 0. Requested JSON
  reports cannot overwrite existing paths and publication failure must fail the
  run. Read-only commands reject apply/output options but may write explicitly
  requested reports. Discovery/result memory still grows with input count.

## Archive and stream operations

- **LC-005, folder packages and repacking:** `folder-to-*` and `archive-to-*`
  for ZIP, TAR, gzip TAR, bzip2 TAR and xz TAR MUST preserve every relative regular
  filename, byte payload and directory, including empty directories. Pack refuses
  source links/special nodes. Repack validates and extracts into private staging
  before producing the selected encoder's output. Verification compares member
  SHA-256 hashes and directory sets. Output extension does not choose the encoder.
  Container metadata and filesystem ownership/ACLs/xattrs/permissions are outside
  this preservation promise.
- **LC-006, standalone compression:** `file-to-gz`, `file-to-bz2`, and
  `file-to-xz` MUST verify decompressed SHA-256 against source bytes before
  publication. Their inverse commands first validate/decompress the source and
  compare the staged output hash. The three `*-verify` commands fully decode and
  report expanded bytes/hash without writes. Corrupt/truncated streams and byte
  expansion over the configured limit fail and do not publish an output.
- **LC-007, archive inspection:** `archive-list` MUST fully read and hash members,
  returning names, sizes, directory flags and regular-file hashes.
  `archive-verify` reports verified member/byte counts; `archive-stats` reports
  member count, stored/expanded bytes and a three-decimal expansion ratio;
  `archive-manifest` maps regular member names to SHA-256. These are complete
  scans, not metadata-only checks. ZIP CRC and native format checks are integrity
  checks; TAR payloads have no intrinsic checksum and require a trusted external
  manifest for later authenticity verification.
- **LC-008, member validation/extraction:** `archive-extract` MUST accept only
  relative regular files/directories, rejecting traversal, absolute names,
  backslashes, colon/drive-like names, NUL, duplicate normalized members, links,
  special files, encryption, truncation and declared-size discrepancies. A
  conventional TAR root-directory entry is ignored. Default expanded limits are
  10 GiB and 100000 members. Extraction writes a new directory only after the
  complete scan succeeds. Native comic extensions reuse this validator and the
  format-specific restrictions in spec 001. Limits do not bound a decoder's
  internal memory/CPU or make it a hostile-input sandbox.

## Local library operations

- **LC-009, inventory and summary:** `library-inventory` MUST report absolute
  and relative paths and file sizes. `library-summary` reports count, total bytes,
  zero-byte count, min/max sizes and lowercase final-extension groups, treating
  trailing-dot names as extensionless consistently across supported Python
  versions. Summary must not read file contents, hash, or invoke codecs. Empty
  discovery is a failure, rather than a fabricated successful zero-file report.
- **LC-010, duplicates:** `library-dupes` MUST report exact SHA-256 groups with
  at least two files, hashing only files whose sizes have another candidate.
  It neither deletes nor hardlinks files; reported duplicates are data, so their
  presence does not itself change a successful exit status to failure.
- **LC-011, manifests:** `hash-manifest` MUST emit relative names, byte sizes,
  and SHA-256 without ambiguous duplicate relative paths. `hash-verify` accepts
  the documented direct manifest and command-response forms, validates schemas
  and checksums, and compares the complete expected/actual key union. Missing,
  changed, and extra files all fail. Uppercase checksum hex normalizes; malformed,
  unsafe, ambiguous or symlink manifest paths fail. A manifest is only as trusted
  as its independently supplied source.
- **LC-012, tree/path findings:** `tree-diff` MUST compare SHA-256 and presence
  across the full union, reporting left-only/right-only/changed relative names.
  Equal files are omitted and ambiguous left-side relative names fail.
  `path-audit` reports control characters, Windows-reserved punctuation,
  components over 240 filename bytes, and trailing dot/space. It does not rename
  or claim exhaustive cross-platform filename validation. Findings from either
  command are successful structured reports, not operational errors.

## MCP and support surfaces

- **LC-013, MCP:** Local newline-delimited JSON-RPC MUST require existing allowed
  roots at startup, initialize before listing/calling tools, and expose only read
  catalog operations without additional path-bearing arguments. Hash verification
  and tree comparison stay excluded. Calls accept only 1–100 string paths,
  reject symlink components and outside-root paths, ignore user config, and run
  one worker with no report paths. Notifications receive no response. Preserve
  the documented protocol negotiation, 1 MiB input and 4 MiB serialized-result
  limits, JSON-only stdout, tool `isError` and JSON-RPC error distinctions.
  Result limits apply after execution. No HTTP, authentication, cancellation,
  arbitrary argument forwarding, write mode, or background tasks are implied.
- **LC-014, maintenance/site:** Catalog generation MUST keep wrappers, tool
  Makefiles, command references and the static site synchronized. Browser search
  combines case-insensitive text with exact category selection and updates the
  count/empty state. Theme toggling retains a stored valid light/dark preference
  or the default light theme, tolerating storage denial. Copying the preview
  command reports clipboard failure and offers manual selection. These controls
  and diagrams do not gain access to media. Existing site/link/accessibility/responsive checks and Pages
  deployment gates remain part of delivery. Architecture diagram sources and
  their evidence are maintained separately from generated catalog output.
  Test fixtures, native codec notices, repository checks, hooks and Spec Kit
  updater templates are supporting contracts, not untracked runtime features.

Changes to existing behavior must update these contracts and the relevant native
fixtures together. New features require their own prospective specification.
